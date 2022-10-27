import base64
import json
import pickle

from fl import mnist_common
from fl.fladmin.fl_admin_gateway_rest_api import FlAdminGatewayRestApi
from fl.flevents.event_processor import EventProcessor
from fl.dto import ModelMetadata
from identity.base.support.utils import log_msg

x_test, y_test = mnist_common.load_test_dataset()


class FlAdminEventProcessor(EventProcessor):
    gateway_rest_api = None

    def __init__(self, gateway_rest_api: FlAdminGatewayRestApi):
        self.gateway_rest_api = gateway_rest_api

    def round_finished(self, event_payload):
        end_round_model = self.gateway_rest_api.get_end_round_model(self.modelId)
        weights = pickle.loads(base64.b64decode(end_round_model.weights))

        model = mnist_common.get_model()
        model.set_weights(weights)
        model.evaluate(x_test, y_test, verbose=1)

    def create_model_metadata(self, event_payload):
        x = json.loads(event_payload)
        metadata = ModelMetadata(**x)
        log_msg(f"EVENT: A model is created. modelId: {metadata.modelId}")

        self.modelId = metadata.modelId
        self.secretsPerClient = metadata.secretsPerClient
        self.trainingRounds = metadata.trainingRounds

    def start_training_event(self, event_payload):
        # Client
        x = json.loads(event_payload)
        metadata = ModelMetadata(**x)
        log_msg(f"EVENT: A model training started. modelId: {metadata.modelId}")
