from fl.control_panel import ControlPanel
from fl.trainer.trainer_gateway_rest_api import TrainerGatewayRestApi


class TrainerControlPanel(ControlPanel):

    def __init__(self, gateway_rest_api: TrainerGatewayRestApi):
        super().__init__(gateway_rest_api)
        self.gateway_rest_api = gateway_rest_api

    def get_personal_info(self):
        return self.gateway_rest_api.get_personal_info_trainer()

    def check_in_func(self):
        self.gateway_rest_api.check_in_trainer()
