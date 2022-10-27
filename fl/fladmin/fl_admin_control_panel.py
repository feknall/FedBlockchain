from random import randint

from fl.config import Config
from fl.fladmin.fl_admin_gateway_rest_api import FlAdminGatewayRestApi
from fl.simple_periodic import SimplePeriodic
from fl.dto import ModelMetadata


class FlAdminControlPanel(SimplePeriodic):

    def __init__(self, gateway_rest_api: FlAdminGatewayRestApi):
        self.gateway_rest_api = gateway_rest_api
        self.modelId = str(randint(0, 100000))

    def create_model_metadata(self):
        cfg = Config()
        body = ModelMetadata(self.modelId, "model1", str(cfg.number_of_clients),
                             str(cfg.number_of_servers),
                             str(cfg.training_rounds))
        self.gateway_rest_api.create_model_metadata(body)

    def start_training(self):
        self.gateway_rest_api.start_training(self.modelId)

    def has_fl_admin_attribute(self):
        self.gateway_rest_api.check_has_fl_admin_attribute()

    def get_personal_info(self):
        self.gateway_rest_api.get_personal_info_fl_admin()
