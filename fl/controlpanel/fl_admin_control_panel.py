from random import randint

from fl.config import Config
from fl.controlpanel.control_panel import ControlPanel
from fl.rest.dto import ModelMetadata


class FlAdminControlPanel(ControlPanel):

    def create_model_metadata(self):
        self.modelId = str(randint(0, 100000))
        cfg = Config()
        body = ModelMetadata(self.modelId, "model1", str(cfg.number_of_clients),
                             str(cfg.number_of_servers),
                             str(cfg.training_rounds))
        self.gateway_rest_api.create_model_metadata(body)
