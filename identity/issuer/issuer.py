import asyncio
import json
import logging
import os
import sys

from aiohttp import ClientError

from identity.base.support.agent import CRED_FORMAT_INDY, CRED_FORMAT_JSON_LD
from identity.base.support.utils import log_json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from identity.base.agent_container import (  # noqa:E402
    arg_parser,
    create_agent_with_args,
    AriesAgent,
)
# from identity.base import (  # noqa:E402
#     CRED_FORMAT_INDY,
#     CRED_FORMAT_JSON_LD,
# )
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


class IssuerAgent(AriesAgent):
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
            prefix="Issuer",
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
    issuer_agent = await create_agent_with_args(args, ident="notClient")

    try:
        log_status(
            "#1 Provision an agent and wallet, get back configuration details"
            + (
                f" (Wallet type: {issuer_agent.wallet_type})"
                if issuer_agent.wallet_type
                else ""
            )
        )
        agent = IssuerAgent(
            "issuer.agent",
            issuer_agent.start_port,
            issuer_agent.start_port + 1,
            genesis_data=issuer_agent.genesis_txns,
            genesis_txn_list=issuer_agent.genesis_txn_list,
            no_auto=issuer_agent.no_auto,
            tails_server_base_url=issuer_agent.tails_server_base_url,
            revocation=issuer_agent.revocation,
            timing=issuer_agent.show_timing,
            multitenant=issuer_agent.multitenant,
            mediation=issuer_agent.mediation,
            wallet_type=issuer_agent.wallet_type,
            seed=issuer_agent.seed,
            aip=issuer_agent.aip,
            endorser_role=issuer_agent.endorser_role,
        )

        simple_schema_name = "personal schema"
        simple_schema_attrs = [
            "name",
            "role"
        ]
        if issuer_agent.cred_type == CRED_FORMAT_INDY:
            issuer_agent.public_did = True
            await issuer_agent.initialize(
                the_agent=agent,
                schema_name=simple_schema_name,
                schema_attrs=simple_schema_attrs,
                create_endorser_agent=(issuer_agent.endorser_role == "author")
                if issuer_agent.endorser_role
                else False,
            )
        elif issuer_agent.cred_type == CRED_FORMAT_JSON_LD:
            issuer_agent.public_did = True
            await issuer_agent.initialize(the_agent=agent)
        else:
            raise Exception("Invalid credential type:" + issuer_agent.cred_type)

        exchange_tracing = False
        options = (
            "    (3) Send Message\n"
            "    (4) Create New Invitation\n"
        )
        options += "    (7) See Issue Credentials\n"
        options += "    (8) Send Offer for a Proposed Credential\n"
        options += "    (9) Issue a Credential for a Credential Request\n"
        options += "    (10) Create a Local DID\n"
        options += "    (11) Accept a Connection Request\n"
        options += "    (12) See Credentials in Wallet\n"
        options += "    (15) List Wallet DIDs\n"
        options += "    (16) Fetch the Current Public DID\n"
        if issuer_agent.endorser_role and issuer_agent.endorser_role == "author":
            options += "    (D) Set Endorser's DID\n"
        options += "    (T) Toggle tracing on credential/proof exchange\n"
        options += "    (X) Exit?\n[1/2/3/4/{}{}T/X] ".format(
            "5/6/" if issuer_agent.revocation else "",
            "W/" if issuer_agent.multitenant else "",
        )
        async for option in prompt_loop(options):
            if option is not None:
                option = option.strip()

            if option is None or option in "xX":
                break
            elif option in "dD" and issuer_agent.endorser_role:
                endorser_did = await prompt("Enter Endorser's DID: ")
                await issuer_agent.agent.admin_POST(
                    f"/transactions/{issuer_agent.agent.connection_id}/set-endorser-info",
                    params={"endorser_did": endorser_did},
                )
            elif option in "tT":
                exchange_tracing = not exchange_tracing
                log_msg(
                    ">>> Credential/Proof Exchange Tracing is {}".format(
                        "ON" if exchange_tracing else "OFF"
                    )
                )
            elif option == "3":
                msg = await prompt("Enter message: ")
                await issuer_agent.agent.admin_POST(
                    f"/connections/{issuer_agent.agent.connection_id}/send-message",
                    {"content": msg},
                )
            elif option == "4":
                log_msg(
                    "Creating a new invitation, please receive "
                    "and accept this invitation using Alice agent"
                )
                invi_rec = await issuer_agent.agent.admin_POST("/connections/create-invitation")
                log_msg(
                    json.dumps(invi_rec["invitation"]), label="Invitation Data:", color=None
                )
                issuer_agent.agent.connection_id = invi_rec["connection_id"]
            elif option == "6" and issuer_agent.revocation:
                try:
                    resp = await issuer_agent.agent.admin_POST(
                        "/revocation/publish-revocations", {}
                    )
                    issuer_agent.agent.log(
                        "Published revocations for {} revocation registr{} {}".format(
                            len(resp["rrid2crid"]),
                            "y" if len(resp["rrid2crid"]) == 1 else "ies",
                            json.dumps([k for k in resp["rrid2crid"]], indent=4),
                        )
                    )
                except ClientError:
                    pass
            elif option == "7":
                try:
                    resp = await issuer_agent.agent.admin_GET("/issue-credential/records")
                    log_json(resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
            elif option == "8":
                try:
                    resp = await issuer_agent.agent.admin_GET("/issue-credential/records")
                    log_json(resp)

                    cred_exchange_id = await prompt("Enter cred-exchange-id: ")
                    get_cred_resp = await issuer_agent.agent.admin_GET("/issue-credential/records/" + cred_exchange_id)
                    log_json(get_cred_resp)

                    confirm = await prompt("Confirm (Yes/No)? ")
                    if confirm.lower() == "yes":
                        send_offer_resp = await issuer_agent.agent.admin_POST(
                            "/issue-credential/records/" + cred_exchange_id + "/send-offer")
                        issuer_agent.agent.log("Offer sent successfully.")
                        log_json(send_offer_resp)
                except Exception:
                    pass
            elif option == "9":
                try:
                    cred_exchange_id = await prompt("Enter cred-exchange-id: ")
                    get_cred_resp = await issuer_agent.agent.admin_GET("/issue-credential/records/" + cred_exchange_id)
                    log_json(get_cred_resp)

                    confirm = await prompt("Confirm (Yes/No)? ")
                    if confirm.lower() == "yes":
                        issue_resp = await issuer_agent.agent.admin_POST(
                            "/issue-credential/records/" + cred_exchange_id + "/issue", {"comment": "hello world!"})
                        issuer_agent.agent.log("Credential issued successfully.")
                        log_json(issue_resp)
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
                    resp = await issuer_agent.agent.admin_POST('/wallet/did/create', create_local_did_req)
                    log_json(resp)
                except ClientError:
                    pass
            elif option == "11":
                try:
                    resp = await issuer_agent.agent.admin_POST(
                        '/connections/' + issuer_agent.agent.connection_id + '/accept-request')
                    log_msg("Connection requested accepted successfully.")
                    log_json(resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
            elif option == "12":
                try:
                    resp = await issuer_agent.agent.admin_GET('/credentials')
                    log_msg("Credentials read successfully.")
                    log_json(resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
            elif option == "15":
                try:
                    wallet_did_resp = await issuer_agent.agent.admin_GET('/wallet/did')
                    log_msg("Wallet DIDs read successfully.")
                    log_json(wallet_did_resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
            elif option == "16":
                try:
                    wallet_did_public_resp = await issuer_agent.agent.admin_GET('/wallet/did/public')
                    log_msg("Wallet DIDs public read successfully.")
                    log_json(wallet_did_public_resp)
                except Exception as e:
                    log_msg("Something went wrong. Error: {}".format(str(e)))
        if issuer_agent.show_timing:
            timing = await issuer_agent.agent.fetch_timing()
            if timing:
                for line in issuer_agent.agent.format_timing(timing):
                    log_msg(line)

    finally:
        terminated = await issuer_agent.terminate()

    await asyncio.sleep(0.1)

    if not terminated:
        os._exit(1)


if __name__ == "__main__":
    parser = arg_parser(ident="notClient", port=8020)
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
                "Issuer remote debugging to "
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
