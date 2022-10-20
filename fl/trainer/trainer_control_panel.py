from fl.simple_periodic import SimplePeriodic
from fl.trainer.trainer_gateway_rest_api import TrainerGatewayRestApi


class TrainerControlPanel(SimplePeriodic):

    def __init__(self, gateway_rest_api: TrainerGatewayRestApi):
        self.gateway_rest_api = gateway_rest_api

    def get_personal_info(self):
        return self.gateway_rest_api.get_personal_info_trainer()

    def check_in_func(self):
        self.gateway_rest_api.check_in_trainer()

    def has_trainer_attribute(self):
        self.gateway_rest_api.check_has_trainer_attribute()
