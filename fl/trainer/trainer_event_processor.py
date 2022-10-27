import base64
import pickle

import numpy as np
import json

from fl import mnist_common
from fl.config import ClientConfig
from fl.flevents.event_processor import EventProcessor
from fl.dto import ModelSecretRequest, ModelMetadata
from fl.trainer.trainer_gateway_rest_api import TrainerGatewayRestApi
from identity.base.support.utils import log_msg

config = ClientConfig()
client_datasets = mnist_common.load_train_dataset(config.number_of_clients, permute=True)


class TrainerEventProcessor(EventProcessor):
    roundCounter = 0
    clientIndex = None
    gateway_rest_api = None

    def __init__(self, client_index, secrets_per_client, gateway_rest_api: TrainerGatewayRestApi):
        self.clientIndex = client_index
        self.gateway_rest_api = gateway_rest_api
        self.secretsPerClient = secrets_per_client

    def train_one_round(self):
        x_train, y_train = client_datasets[self.clientIndex][0], client_datasets[self.clientIndex][1]
        model = mnist_common.get_model()

        if self.roundWeight is not None:
            log_msg("Using weights of previous round.")
            model.set_weights(self.roundWeight)

        model.fit(x_train, y_train, epochs=config.epochs, batch_size=config.batch_size, verbose=config.verbose,
                  validation_split=config.validation_split, shuffle=True)

        layer_dict, layer_shape, shares_dict = {}, {}, {}
        data = np.array(model.get_weights())
        no_of_layers = len(data)
        for layer_index in range(no_of_layers):
            layer_dict[layer_index] = data[layer_index]
            layer_shape[layer_index] = data[layer_index].shape

        for layer_index in range(no_of_layers):
            x = np.copy(layer_dict[layer_index])
            shares_dict[layer_index] = np.random.random(
                size=(self.secretsPerClient,) + layer_shape[layer_index]).astype(np.float64)

            for server_index in range(self.secretsPerClient - 1):
                shares_dict[layer_index][server_index] = np.random.random(size=layer_shape[layer_index]).astype(
                    np.float32)
                x = np.subtract(x, shares_dict[layer_index][server_index])
            shares_dict[layer_index][self.secretsPerClient - 1] = x

        all_servers = []
        for server_index in range(self.secretsPerClient):
            all_servers.append({})

        for server_index in range(self.secretsPerClient):
            for layer_index in range(len(shares_dict)):
                all_servers[server_index][layer_index] = shares_dict[layer_index][server_index]

        weights1 = base64.b64encode(pickle.dumps(all_servers[0])).decode()
        weights2 = base64.b64encode(pickle.dumps(all_servers[1])).decode()
        dataset_size = client_datasets[self.clientIndex][0].shape[0]
        model_secret = ModelSecretRequest(self.modelId, dataset_size, weights1, weights2)

        self.gateway_rest_api.add_model_secret(model_secret)

        log_msg("Secrets are sent.")

        log_msg(f"Round {self.roundCounter} completed.")

        self.roundCounter = self.roundCounter + 1
        log_msg("Waiting...")

        log_msg(f"Start training...")

    def start_training_event(self, event_payload):
        client_is_selected = self.gateway_rest_api.check_i_am_selected_for_round()
        if not client_is_selected:
            log_msg("It's not my turn. Ignoring...")
            return
        x = json.loads(event_payload)
        metadata = ModelMetadata(**x)
        log_msg(f"EVENT: A model training started. modelId: {metadata.modelId}")
        self.modelId = metadata.modelId
        self.train_one_round()

    def round_finished(self, event_payload):
        client_is_selected = self.gateway_rest_api.check_i_am_selected_for_round()
        if not client_is_selected:
            log_msg("It's not my turn. Ignoring...")
            return

        end_round_model = self.gateway_rest_api.get_end_round_model(self.modelId)
        self.roundWeight = pickle.loads(base64.b64decode(end_round_model.weights))
        self.train_one_round()

    def training_finished(self, event_payload):
        log_msg("Training finiiiiiiiiiiiiiiished :D")
