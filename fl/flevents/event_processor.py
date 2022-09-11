import base64
import json
import pickle

import numpy as np

from identity.base.support.utils import log_msg
from fl import flcommon
from fl import mnist_common
from fl.config import ClientConfig
from fl.rest.dto import ModelMetadata, ModelSecretRequest, ModelSecretResponse, AggregatedSecret, \
    EndRoundModel
from fl.rest.gateway_rest_api import GatewayRestApi

config = ClientConfig()
client_datasets = mnist_common.load_train_dataset(config.number_of_clients, permute=True)
x_test, y_test = mnist_common.load_test_dataset()


class EventProcessor:
    modelId = None
    clientId1 = None
    clientId2 = None
    secretsPerClient = None
    trainingRounds = None
    clientIndex = None
    roundWeight = None
    gateway_rest_api = None

    def __init__(self, client_id_1, client_id_2, client_index, gateway_rest_api: GatewayRestApi):
        self.clientId1 = client_id_1
        self.clientId2 = client_id_2
        self.clientIndex = client_index
        self.gateway_rest_api = gateway_rest_api

    def all_secrets_received(self, event_payload):
        # Aggregator
        pass

    def aggregation_finished(self, event_payload):
        # LeadAggregator
        pass

    def round_finished(self, event_payload):
        # Clients
        pass

    def training_finished(self, event_payload):
        # All
        pass

    def model_secret_added(self, event_payload):
        # Audit
        pass

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

    def aggregated_secret_added_event(self, event_payload):
        pass


class FlAdminEventProcessor(EventProcessor):

    def round_finished(self, event_payload):
        end_round_model = self.gateway_rest_api.get_end_round_model(self.modelId)
        weights = pickle.loads(base64.b64decode(end_round_model.weights))

        model = mnist_common.get_model(flcommon.input_shape)
        model.set_weights(weights)
        model.evaluate(x_test, y_test, verbose=1)


class TrainerEventProcessor(EventProcessor):
    roundCounter = 0

    def train_one_round(self):
        x_train, y_train = client_datasets[self.clientIndex][0], client_datasets[self.clientIndex][1]
        model = mnist_common.get_model(flcommon.input_shape)

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


class AggregatorEventProcessor(EventProcessor):
    current_round = -1

    def model_secret_added(self, event_payload):
        x = json.loads(event_payload)
        model_secret = ModelSecretResponse(**x)
        log_msg(f"EVENT: A model secret is added. modelId: {model_secret.modelId}")

        if self.current_round >= model_secret.round:
            log_msg("Already started. Ignoring...")
            return

        if not self.gateway_rest_api.check_all_secrets_received(self.modelId):
            log_msg("Waiting for more secrets...")
            return

        log_msg("Aggregator is started :)")

        self.current_round = model_secret.round

        secrets = self.gateway_rest_api.get_model_secrets_for_current_round(self.modelId)

        clients_secret = []
        dataset_size_list = []
        for secret in secrets:
            clients_secret.append(pickle.loads(base64.b64decode(secret.weights)))
            dataset_size_list.append(secret.datasetSize)
        total_dataset_size = sum(dataset_size_list)

        log_msg(f"Trying to aggregate {len(clients_secret)} secrets")

        model = {}
        for layer_index in range(len(clients_secret[0])):
            alpha_list = []
            for client_index in range(len(clients_secret)):
                alpha = clients_secret[client_index][layer_index] * (
                        dataset_size_list[client_index] / total_dataset_size)
                alpha_list.append(alpha)
            model[layer_index] = np.array(alpha_list).sum(axis=0, dtype=np.float64)

        model_byte = base64.b64encode(pickle.dumps(model)).decode()

        aggregated_secret = AggregatedSecret(self.modelId, model_byte)

        self.gateway_rest_api.add_aggregated_secret(aggregated_secret)

        log_msg("Aggregation finished successfully.")


class LeadAggregatorEventProcessor(EventProcessor):
    current_round = -1

    def aggregated_secret_added_event(self, event_payload):
        x = json.loads(event_payload)
        aggregated_secret = AggregatedSecret(**x)
        log_msg(f"EVENT: A aggregated secret for a model is added. modelId: {aggregated_secret.modelId}")

        if self.current_round >= aggregated_secret.round:
            log_msg("Already started. Ignoring...")
            return

        if not self.gateway_rest_api.check_all_aggregated_secrets_received(self.modelId):
            log_msg("Waiting for more aggregated secrets...")
            return
        log_msg("Lead aggregator is started :)")

        self.current_round = aggregated_secret.round

        aggregated_secrets = self.gateway_rest_api.get_aggregated_secrets_for_current_round(self.modelId)

        decoded_aggregated_secrets = []
        for aggregated_secret in aggregated_secrets:
            decoded_aggregated_secrets.append(pickle.loads(base64.b64decode(aggregated_secret.weights)))

        log_msg(f"Trying to aggregate {len(decoded_aggregated_secrets)} secrets")

        model = {}
        for layer_index in range(len(decoded_aggregated_secrets[0])):
            layer_list = []
            for server_index in range(self.secretsPerClient):
                layer_list.append(decoded_aggregated_secrets[server_index][layer_index])
            model[layer_index] = np.array(layer_list).sum(axis=0, dtype=np.float64)

        model_byte = base64.b64encode(pickle.dumps(model)).decode()
        end_round_model = EndRoundModel(self.modelId, model_byte)

        self.gateway_rest_api.add_end_round_model(end_round_model)

        log_msg("Lead aggregation finished successfully.")
