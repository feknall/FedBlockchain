import asyncio
import base64
import binascii
import json
import logging
import os
import sys
from urllib.parse import urlparse

from identity.common.fabric_ca_args_parser import FabricCaArgParser
from identity.common.fabric_ca_client_wrapper import FabricCaClientWrapper

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from identity.base.agent_container import (  # noqa:E402
    arg_parser,
    create_agent_with_args,
    AriesAgent,
)
from identity.base.support.utils import (  # noqa:E402
    check_requires,
    log_msg,
    log_status,
    log_timer,
    prompt,
    prompt_loop, log_json,
)

logging.basicConfig(level=logging.WARNING)
LOGGER = logging.getLogger(__name__)


class ClientAgent(AriesAgent):
    def __init__(
            self,
            ident: str,
            http_port: int,
            admin_port: int,
            no_auto: bool = False,
            aip: int = 20,
            endorser_role: str = None,
            **kwargs,
    ):
        super().__init__(
            ident,
            http_port,
            admin_port,
            prefix="Client",
            no_auto=no_auto,
            seed=None,
            aip=aip,
            endorser_role=endorser_role,
            **kwargs,
        )
        self.connection_id = None
        self._connection_ready = None
        self.cred_state = {}

    async def detect_connection(self):
        await self._connection_ready
        self._connection_ready = None

    @property
    def connection_ready(self):
        return self._connection_ready.done() and self._connection_ready.result()


async def input_invitation(agent_container):
    agent_container.agent._connection_ready = asyncio.Future()
    async for details in prompt_loop("Invite details: "):
        b64_invite = None
        try:
            url = urlparse(details)
            query = url.query
            if query and "c_i=" in query:
                pos = query.index("c_i=") + 4
                b64_invite = query[pos:]
            elif query and "oob=" in query:
                pos = query.index("oob=") + 4
                b64_invite = query[pos:]
            else:
                b64_invite = details
        except ValueError:
            b64_invite = details

        if b64_invite:
            try:
                padlen = 4 - len(b64_invite) % 4
                if padlen <= 2:
                    b64_invite += "=" * padlen
                invite_json = base64.urlsafe_b64decode(b64_invite)
                details = invite_json.decode("utf-8")
            except binascii.Error:
                pass
            except UnicodeDecodeError:
                pass

        if details:
            try:
                details = json.loads(details)
                break
            except json.JSONDecodeError as e:
                log_msg("Invalid invitation:", str(e))

    with log_timer("Connect duration:"):
        connection = await agent_container.input_invitation(details, wait=True)


async def send_proposal(agent_container):
    agent_container.agent._connection_ready = asyncio.Future()


async def main(args):
    client_agent = await create_agent_with_args(args, ident="client")

    try:
        log_status(
            "#7 Provision an agent and wallet, get back configuration details"
            + (
                f" (Wallet type: {client_agent.wallet_type})"
                if client_agent.wallet_type
                else ""
            )
        )
        agent = ClientAgent(
            "client.agent",
            client_agent.start_port,
            client_agent.start_port + 1,
            genesis_data=client_agent.genesis_txns,
            genesis_txn_list=client_agent.genesis_txn_list,
            no_auto=client_agent.no_auto,
            tails_server_base_url=client_agent.tails_server_base_url,
            revocation=client_agent.revocation,
            timing=client_agent.show_timing,
            multitenant=client_agent.multitenant,
            mediation=client_agent.mediation,
            wallet_type=client_agent.wallet_type,
            aip=client_agent.aip,
            endorser_role=client_agent.endorser_role,
        )

        await client_agent.initialize(the_agent=agent)

        # log_status("#9 Input verifier.py invitation details")
        # await input_invitation(client_agent)

        options = "    (3) Send Message\n" \
                  "    (4) Receive New Invitation\n" \
                  "    (5) Propose a Credential \n" \
                  "    (7) See Issue Credential Records\n" \
                  "    (8) Send Request for a Credential Offer\n" \
                  "    (9) Store an Issued Credential\n" \
                  "    (10) Create a Local DID\n" \
                  "    (11) Accept an Invitation\n" \
                  "    (12) See Credentials in Wallet\n" \
                  "    (13) See Proof Records\n" \
                  "    (14) Send Presentation for a Present Proof\n" \
                  "    (15) List Wallet DIDs\n" \
                  "    (16) Fetch the Current Public DID\n" \
                  "    (17) Enroll for Fabric\n"

        if client_agent.endorser_role and client_agent.endorser_role == "author":
            options += "    (D) Set Endorser's DID\n"
        if client_agent.multitenant:
            options += "    (W) Create and/or Enable Wallet\n"
        options += "    (X) Exit?\n[3/4/{}X] ".format(
            "W/" if client_agent.multitenant else "",
        )
        async for option in prompt_loop(options):
            if option is not None:
                option = option.strip()

            if option is None or option in "xX":
                break

            elif option in "dD" and client_agent.endorser_role:
                endorser_did = await prompt("Enter Endorser's DID: ")
                await client_agent.agent.admin_POST(
                    f"/transactions/{client_agent.agent.connection_id}/set-endorser-info",
                    params={"endorser_did": endorser_did, "endorser_name": "endorser"},
                )

            elif option == "3":
                msg = await prompt("Enter message: ")
                if msg:
                    await client_agent.agent.admin_POST(
                        f"/connections/{client_agent.agent.connection_id}/send-message",
                        {"content": msg},
                    )

            elif option == "4":
                try:
                    log_status("Input new invitation details")
                    invitation = await prompt("Invitation details:")
                    recv_invt_resp = await client_agent.agent.admin_POST("/connections/receive-invitation", invitation)
                    log_msg("Invitation received successfully.")
                    client_agent.agent.connection_id = recv_invt_resp["connection_id"]
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
            elif option == "5":
                try:
                    name = await prompt("Enter your name: ")
                    role = await prompt("Enter your role (trainer/flAdmin/aggregator/leadAggregator): ")

                    cred_attrs = [{"name": "name", "value": "{}".format(name)},
                                  {"name": "role", "value": "{}".format(role)}]

                    proposal_request = {
                        "connection_id": client_agent.agent.connection_id,
                        "credential_proposal": {
                            "attributes": cred_attrs
                        }
                    }
                    proposal_resp = await client_agent.agent.admin_POST("/issue-credential/send-proposal",
                                                                       data=proposal_request)
                    cred_ex_id = proposal_resp["credential_exchange_id"]
                    client_agent.agent.cred_ex_id = cred_ex_id
                    log_msg(f"Credential proposal sent successfully. credential_exchange_id: {cred_ex_id}")
                    log_json(proposal_resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
            elif option == "7":
                try:
                    resp = await client_agent.agent.admin_GET("/issue-credential/records")
                    log_json(resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
            elif option == "8":
                try:
                    get_cred_resp = await client_agent.agent.admin_GET(
                        "/issue-credential/records/" + client_agent.agent.cred_ex_id)
                    log_json(get_cred_resp)

                    confirm = await prompt("Confirm (Yes/No)? ")
                    if confirm.lower() == "yes":
                        resp = await client_agent.agent.admin_POST(
                            "/issue-credential/records/" + client_agent.agent.cred_ex_id + "/send-request")
                        log_msg(f"Credential request sent successfully.")
                        log_json(resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
            elif option == "9":
                try:
                    get_cred_resp = await client_agent.agent.admin_GET(
                        "/issue-credential/records/" + client_agent.agent.cred_ex_id)
                    log_json(get_cred_resp)

                    confirm = await prompt("Confirm (Yes/No)? ")
                    credential_id = await prompt("Enter an ID for storing the credential: ")
                    if confirm.lower() == "yes":
                        personal_credential_req = {"credential_id": credential_id}
                        store_resp = await client_agent.agent.admin_POST(
                            "/issue-credential/records/" + client_agent.agent.cred_ex_id + "/store",
                            personal_credential_req)
                        log_msg("Issued credential stored successfully.")
                        log_json(store_resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
            elif option == "10":
                try:
                    create_local_did_req = {
                        "method": "sov",
                        "options": {
                            "key_type": "ed25519"
                        }
                    }
                    resp = await client_agent.agent.admin_POST('/wallet/did/create', create_local_did_req)
                    log_msg(resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
            elif option == "11":
                try:
                    accept_resp = await client_agent.agent.admin_POST(
                        "/connections/" + client_agent.agent.connection_id + "/accept-invitation")
                    log_msg("Invitation accepted successfully.")
                    log_json(accept_resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
            elif option == "12":
                try:
                    resp = await client_agent.agent.admin_GET('/credentials')
                    log_msg("Credentials read successfully.")
                    log_json(resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
            elif option == "13":
                try:
                    present_proof_rec_resp = await client_agent.agent.admin_GET('/present-proof/records')
                    log_msg("Present proof records read successfully.")
                    log_json(present_proof_rec_resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
            elif option == "14":
                try:
                    present_proof_rec_resp = await client_agent.agent.admin_GET('/present-proof/records')
                    log_json(present_proof_rec_resp)
                    pres_ex_id = await prompt("Enter pres-ex-id: ")
                    cred_id = await prompt("Enter cred-id in wallet: ")

                    send_present_req = {
                        "requested_predicates": {},
                        "self_attested_attributes": {},
                        "requested_attributes": {
                            "additionalProp1": {
                                "revealed": True,
                                "cred_id": cred_id
                            },
                            "additionalProp2": {
                                "revealed": True,
                                "cred_id": cred_id
                            }
                        }
                    }
                    send_present_resp = await client_agent.agent.admin_POST(
                        '/present-proof/records/' + pres_ex_id + '/send-presentation', send_present_req)
                    log_msg("Proof presentation sent successfully.")
                    log_json(send_present_resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
            elif option == "15":
                try:
                    wallet_did_resp = await client_agent.agent.admin_GET('/wallet/did')
                    log_msg("Wallet DIDs read successfully.")
                    log_json(wallet_did_resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
            elif option == "16":
                try:
                    wallet_did_public_resp = await client_agent.agent.admin_GET('/wallet/did/public')
                    log_msg("Wallet DIDs public read successfully.")
                    log_json(wallet_did_public_resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
            elif option == "17":
                try:
                    fabric_ca_arg_parser = FabricCaArgParser(args)
                    enrollment_id = await prompt("Enter enrollment id: ")
                    enrollment_secret = await prompt("Enter enrollment secret: ")
                    fabric_ca_client_wrapper = FabricCaClientWrapper(fabric_ca_arg_parser.home,
                                                                      fabric_ca_arg_parser.address,
                                                                      fabric_ca_arg_parser.port,
                                                                      fabric_ca_arg_parser.caname,
                                                                      fabric_ca_arg_parser.tls_certfiles,
                                                                      enrollment_id,
                                                                      enrollment_secret)
                    fabric_ca_client_wrapper.enroll_msp(fabric_ca_arg_parser.msp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
        if client_agent.show_timing:
            timing = await client_agent.agent.fetch_timing()
            if timing:
                for line in client_agent.agent.format_timing(timing):
                    log_msg(line)

    finally:
        terminated = await client_agent.terminate()

    await asyncio.sleep(0.1)

    if not terminated:
        os._exit(1)


if __name__ == "__main__":
    parser = arg_parser(ident="client", port=8030)
    args = parser.parse_args()

    ENABLE_PYDEVD_PYCHARM = os.getenv("ENABLE_PYDEVD_PYCHARM", "").lower()
    ENABLE_PYDEVD_PYCHARM = ENABLE_PYDEVD_PYCHARM and ENABLE_PYDEVD_PYCHARM not in (
        "false",
        "0",
    )
    PYDEVD_PYCHARM_HOST = os.getenv("PYDEVD_PYCHARM_HOST", "localhost")
    PYDEVD_PYCHARM_CONTROLLER_PORT = int(
        os.getenv("PYDEVD_PYCHARM_CONTROLLER_PORT", 5001)
    )

    if ENABLE_PYDEVD_PYCHARM:
        try:
            import pydevd_pycharm

            print(
                "Client remote debugging to "
                f"{PYDEVD_PYCHARM_HOST}:{PYDEVD_PYCHARM_CONTROLLER_PORT}"
            )
            pydevd_pycharm.settrace(
                host=PYDEVD_PYCHARM_HOST,
                port=PYDEVD_PYCHARM_CONTROLLER_PORT,
                stdoutToServer=True,
                stderrToServer=True,
                suspend=False,
            )
        except ImportError:
            print("pydevd_pycharm library was not found")

    check_requires(args)

    try:
        asyncio.get_event_loop().run_until_complete(main(args))
    except KeyboardInterrupt:
        os._exit(1)
