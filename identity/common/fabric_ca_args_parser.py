from identity.base.support.utils import log_msg


class FabricCaArgParser:
    home = ""
    id = ""
    secret = ""
    address = ""
    port = ""
    tls_certfiles = ""
    caname = ""
    msp = ""

    def __init__(self, args):
        self.home = args.fabric_ca_client_home
        log_msg(f"Fabric Ca Client Home: {self.home}")

        self.id = args.fabric_ca_client_enrollment_id
        log_msg(f"Fabric Ca Client Enrollment ID: {self.id}")

        self.secret = args.fabric_ca_client_enrollment_secret
        log_msg(f"Fabric Ca Client Enrollment Secret: {self.secret}")

        self.caname = args.fabric_ca_client_ca_name
        log_msg(f"Fabric Ca Client Ca Name: {self.caname}")

        self.address = args.fabric_ca_client_ca_address
        log_msg(f"Fabric Ca Client Ca Address: {self.address}")

        self.port = args.fabric_ca_client_ca_port
        log_msg(f"Fabric Ca Client Ca Port: {self.port}")

        self.tls_certfiles = args.fabric_ca_client_tls_certfiles
        log_msg(f"Fabric Ca Enrollment ID: {self.tls_certfiles}")

        self.msp = args.fabric_ca_client_msp
        log_msg(f"Fabric Ca MSP: {self.msp}")
