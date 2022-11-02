import asyncio
import json
import logging
import os
import sys
from random import randint

from aiohttp import ClientError

from identity import role_constatns
from identity.base.support.agent import CRED_FORMAT_INDY, CRED_FORMAT_JSON_LD
from identity.base.support.utils import log_json
from identity.common.fabric_ca_args_parser import FabricCaArgParser
from identity.common.fabric_ca_client_wrapper import FabricCaClientWrapper

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from identity.base.agent_container import (  # noqa:E402
    arg_parser,
    create_agent_with_args,
    AriesAgent,
)

from identity.base.support.utils import (  # noqa:E402
    log_msg,
    log_status,
    prompt,
    prompt_loop,
)

CRED_PREVIEW_TYPE = "https://didcomm.org/issue-credential/2.0/credential-preview"
SELF_ATTESTED = os.getenv("SELF_ATTESTED")
TAILS_FILE_COUNT = int(os.getenv("TAILS_FILE_COUNT", 100))

logging.basicConfig(level=logging.WARNING)
LOGGER = logging.getLogger(__name__)


class VerifierAgent(AriesAgent):
    def __init__(
            self,
            ident: str,
            http_port: int,
            admin_port: int,
            no_auto: bool = False,
            endorser_role: str = None,
            revocation: bool = False,
            **kwargs,
    ):
        super().__init__(
            ident,
            http_port,
            admin_port,
            prefix="Verifier",
            no_auto=no_auto,
            endorser_role=endorser_role,
            revocation=revocation,
            **kwargs,
        )
        self.connection_id = None
        self._connection_ready = None
        self.cred_state = {}
        # TODO define a dict to hold credential attributes
        # based on cred_def_id
        self.cred_attrs = {}

    async def detect_connection(self):
        await self._connection_ready
        self._connection_ready = None

    @property
    def connection_ready(self):
        return self._connection_ready.done() and self._connection_ready.result()


async def main(args):
    fabric_ca_arg_parser = FabricCaArgParser(args)
    fabric_ca_client_wrapper = FabricCaClientWrapper(fabric_ca_arg_parser.home,
                                                     fabric_ca_arg_parser.address,
                                                     fabric_ca_arg_parser.port,
                                                     fabric_ca_arg_parser.caname,
                                                     fabric_ca_arg_parser.tls_certfiles,
                                                     fabric_ca_arg_parser.id,
                                                     fabric_ca_arg_parser.secret)
    fabric_ca_client_wrapper.enroll()

    verifier_agent = await create_agent_with_args(args, ident="notClient")

    try:
        log_status(
            "#1 Provision an agent and wallet, get back configuration details"
            + (
                f" (Wallet type: {verifier_agent.wallet_type})"
                if verifier_agent.wallet_type
                else ""
            )
        )
        agent = VerifierAgent(
            "verifier.agent",
            verifier_agent.start_port,
            verifier_agent.start_port + 1,
            genesis_data=verifier_agent.genesis_txns,
            genesis_txn_list=verifier_agent.genesis_txn_list,
            no_auto=verifier_agent.no_auto,
            tails_server_base_url=verifier_agent.tails_server_base_url,
            revocation=verifier_agent.revocation,
            timing=verifier_agent.show_timing,
            multitenant=verifier_agent.multitenant,
            mediation=verifier_agent.mediation,
            wallet_type=verifier_agent.wallet_type,
            seed=verifier_agent.seed,
            aip=verifier_agent.aip,
            endorser_role=verifier_agent.endorser_role,
        )

        simple_schema_name = "personal schema"
        simple_schema_attrs = [
            "name",
            "role"
        ]
        if verifier_agent.cred_type == CRED_FORMAT_INDY:
            verifier_agent.public_did = True
            await verifier_agent.initialize(
                the_agent=agent,
                schema_name=simple_schema_name,
                schema_attrs=simple_schema_attrs,
                create_endorser_agent=(verifier_agent.endorser_role == "author")
                if verifier_agent.endorser_role
                else False,
            )
        elif verifier_agent.cred_type == CRED_FORMAT_JSON_LD:
            verifier_agent.public_did = True
            await verifier_agent.initialize(the_agent=agent)
        else:
            raise Exception("Invalid credential type:" + verifier_agent.cred_type)

        exchange_tracing = False
        options = (
            "    (2) Send Proof Request\n"
            "    (3) Send Message\n"
            "    (4) Create New Invitation\n"
        )
        options += "    (10) Create a Local DID\n"
        options += "    (11) Accept a Connection Request\n"
        options += "    (12) See Credentials in Wallet\n"
        options += "    (13) See Proof Records\n"
        options += "    (14) Verify a Proof Presentation\n"
        options += "    (15) List Wallet DIDs\n"
        options += "    (16) Fetch the Current Public DID\n"
        options += "    (17) Register for Fabric\n"
        if verifier_agent.endorser_role and verifier_agent.endorser_role == "author":
            options += "    (D) Set Endorser's DID\n"
        options += "    (T) Toggle tracing on credential/proof exchange\n"
        options += "    (X) Exit?\n[1/2/3/4/{}{}T/X] ".format(
            "5/6/" if verifier_agent.revocation else "",
            "W/" if verifier_agent.multitenant else "",
        )
        async for option in prompt_loop(options):
            if option is not None:
                option = option.strip()

            if option is None or option in "xX":
                break

            elif option in "dD" and verifier_agent.endorser_role:
                endorser_did = await prompt("Enter Endorser's DID: ")
                await verifier_agent.agent.admin_POST(
                    f"/transactions/{verifier_agent.agent.connection_id}/set-endorser-info",
                    params={"endorser_did": endorser_did},
                )

            elif option in "tT":
                exchange_tracing = not exchange_tracing
                log_msg(
                    ">>> Credential/Proof Exchange Tracing is {}".format(
                        "ON" if exchange_tracing else "OFF"
                    )
                )

            elif option == "2":
                try:
                    proof_request = {
                        "name": "Proof of Personal Information",
                        "version": "1.0",
                        "requested_attributes": {
                            "additionalProp1": {
                                "name": "name"
                            },
                            "additionalProp2": {
                                "name": "role"
                            }
                        },
                        "requested_predicates": {
                        },
                    }

                    present_proof_req = {
                        "comment": "a random string",
                        "connection_id": verifier_agent.agent.connection_id,
                        "proof_request": proof_request
                    }

                    proof_resp = await verifier_agent.agent.admin_POST("/present-proof/send-request", present_proof_req)
                    log_msg("Proof request sent successfully.")
                    log_json(proof_resp)
                except Exception as e:
                    log_msg("Something went wrong. error: {}".format(e))

            elif option == "3":
                msg = await prompt("Enter message: ")
                await verifier_agent.agent.admin_POST(
                    f"/connections/{verifier_agent.agent.connection_id}/send-message",
                    {"content": msg},
                )

            elif option == "4":
                log_msg(
                    "Creating a new invitation, please receive "
                    "and accept this invitation using Alice agent"
                )
                invi_rec = await verifier_agent.agent.admin_POST("/connections/create-invitation")
                log_msg(
                    json.dumps(invi_rec["invitation"]), label="Invitation Data:", color=None
                )
                verifier_agent.agent.connection_id = invi_rec["connection_id"]

            elif option == "10":
                try:
                    create_local_did_req = {
                        "method": "sov",
                        "options": {
                            "key_type": "ed25519"
                        }
                    }
                    resp = await verifier_agent.agent.admin_POST('/wallet/did/create', create_local_did_req)
                    log_json(resp)
                except ClientError:
                    pass

            elif option == "11":
                try:
                    resp = await verifier_agent.agent.admin_POST(
                        '/connections/' + verifier_agent.agent.connection_id + '/accept-request')
                    log_msg("Connection requested accepted successfully.")
                    log_json(resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))

            elif option == "12":
                try:
                    resp = await verifier_agent.agent.admin_GET('/credentials')
                    log_msg("Credentials read successfully.")
                    log_json(resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))

            elif option == "13":
                try:
                    present_proof_rec_resp = await verifier_agent.agent.admin_GET('/present-proof/records')
                    log_msg("Present proof records read successfully.")
                    log_json(present_proof_rec_resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))

            elif option == "14":
                try:
                    present_proof_rec_resp = await verifier_agent.agent.admin_GET('/present-proof/records')
                    log_msg("Present proof records read successfully.")
                    log_json(present_proof_rec_resp)

                    pres_ex_id = await prompt("Enter pres-ex-id: ")
                    verify_resp = await verifier_agent.agent.admin_POST(
                        '/present-proof/records/' + pres_ex_id + '/verifier-presentation')
                    log_json(verify_resp)
                    if verify_resp['verified'] == "true":
                        log_msg("Identity verified successfully.")

                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))

            elif option == "15":
                try:
                    wallet_did_resp = await verifier_agent.agent.admin_GET('/wallet/did')
                    log_msg("Wallet DIDs read successfully.")
                    log_json(wallet_did_resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))

            elif option == "16":
                try:
                    wallet_did_public_resp = await verifier_agent.agent.admin_GET('/wallet/did/public')
                    log_msg("Wallet DIDs public read successfully.")
                    log_json(wallet_did_public_resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))

            elif option == "17":
                try:
                    role = await prompt("Enter role (trainer/flAdmin/leadAggregator/aggregator):")
                    random_number = str(randint(0, 100000))

                    if role == role_constatns.ROLE_TRAINER:
                        id_name = "trainer" + random_number
                        id_secret = "trainer" + random_number + "pw"
                        fabric_ca_client_wrapper.register_trainer(id_name, id_secret)
                    elif role == role_constatns.ROLE_AGGREGATOR:
                        id_name = "aggregator" + random_number
                        id_secret = "aggregator" + random_number + "pw"
                        fabric_ca_client_wrapper.register_aggregator(id_name, id_secret)
                    elif role == role_constatns.ROLE_FL_ADMIN:
                        id_name = "flAdmin" + random_number
                        id_secret = "flAdmin" + random_number + "pw"
                        fabric_ca_client_wrapper.register_fl_admin(id_name, id_secret)
                    elif role == role_constatns.ROLE_LEAD_AGGREGATOR:
                        id_name = "leadAggregator" + random_number
                        id_secret = "leadAggregator" + random_number + "pw"
                        fabric_ca_client_wrapper.register_lead_aggregator(id_name, id_secret)
                    else:
                        log_msg("Unknown role. There is something wrong. Ignoring...")
                        return
                    msg = f"id_name: {id_name}, id_secret: {id_secret}"
                    await verifier_agent.agent.admin_POST(
                        f"/connections/{verifier_agent.agent.connection_id}/send-message",
                        {"content": msg})
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))

    finally:
        terminated = await verifier_agent.terminate()

    await asyncio.sleep(0.1)

    if not terminated:
        os._exit(1)


if __name__ == "__main__":
    parser = arg_parser(ident="notClient", port=8040)
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
                "Verifier remote debugging to "
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

    try:
        asyncio.get_event_loop().run_until_complete(main(args))
    except KeyboardInterrupt:
        os._exit(1)
