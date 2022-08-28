
import json
import pickle
import threading

import base64
import numpy as np


from base.support.utils import log_msg, log_json
from fl import flcommon
from fl import mnist_common
from fl.config import ClientConfig

from rest.dto import ModelMetadata, ModelSecret, TrainerMetadata


config = ClientConfig()
client_datasets = mnist_common.load_train_dataset(config.number_of_clients, permute=True)


class EventProcessor:
    modelId = None
    clientId1 = None
    clientId2 = None
    secretsPerClient = None
    trainingRounds = None
    clientIndex = None
    roundWeight = None
    roundSelectedFor = None
    gateway_rest_api = None

    def __init__(self, client_id_1, client_id_2, client_index, gateway_rest_api):
        self.clientId1 = client_id_1
        self.clientId2 = client_id_2
        self.clientIndex = client_index
        self.gateway_rest_api = gateway_rest_api

    def all_secrets_received(self, event_payload):
        # Aggregator
        x = json.loads(event_payload)
        model_secret = ModelSecret(**x)
        print(model_secret.modelId)

    def aggregation_finished(self, event_payload):
        # LeadAggregator
        pass

    def round_finished(self, event_payload):
        # Clients
        pass

    def round_and_training_finished(self, event_payload):
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

    def client_selected_for_round_event(self, event_payload):
        x = json.loads(event_payload)
        metadata = TrainerMetadata(**x)
        log_msg(f"EVENT: A client is selected for training. clientId: {metadata.clientId}")

        if metadata.clientId != self.clientId1 and metadata.clientId != self.clientId2:
            log_msg("Ignoring...")
            return

        self.roundSelectedFor = metadata.roundSelectedFor

        log_msg(f"Start training...")

        x_train, y_train = client_datasets[self.clientIndex][0][:100], client_datasets[self.clientIndex][1][:100]
        model = mnist_common.get_model(flcommon.input_shape)

        if self.roundSelectedFor > 0:
            model.set_weights(self.roundWeight)

        model.fit(x_train, y_train, epochs=config.epochs, batch_size=config.batch_size, verbose=config.verbose,
                  validation_split=config.validation_split)

        round_weight = np.array(model.get_weights())

        all_servers = []
        servers_model = []

        for server_index in range(self.secretsPerClient):
            all_servers.append({})
            servers_model.append({})

        # Each client divides its model to some secrets and sends secrets to the servers
        layer_dict, layer_shape, shares_dict = {}, {}, {}
        data = round_weight
        no_of_layers = len(data)
        for layer_index in range(no_of_layers):
            layer_dict[layer_index] = data[layer_index]
            layer_shape[layer_index] = data[layer_index].shape

        for layer_index in range(no_of_layers):
            x = layer_dict[layer_index]
            shares_dict[layer_index] = np.random.random(size=(self.secretsPerClient,) + layer_shape[layer_index])

            for server_index in range(0, self.secretsPerClient - 1):
                shares_dict[layer_index][server_index] = np.random.random(size=layer_shape[layer_index])
                x = x - shares_dict[layer_index][server_index]
            shares_dict[layer_index][self.secretsPerClient - 1] = x

        for server_index in range(self.secretsPerClient):
            for layer_index in range(len(shares_dict)):
                all_servers[server_index][layer_index] = shares_dict[layer_index][server_index]

        weights1 = str(base64.b64encode(pickle.dumps(all_servers[0])))
        weights2 = str(base64.b64encode(pickle.dumps(all_servers[1])))

        model_secret = ModelSecret(self.modelId, self.roundSelectedFor, weights1, weights2)
        self.gateway_rest_api.add_model_secret(model_secret)

        print("Secrets are sent.")

        print(f"Round {self.roundSelectedFor} completed.")
        print("Waiting...")

# ------------------ Begin Client Check In ------------------

# ------------------ End Client Check In ------------------

# ------------------ Begin Process Socket Events ------------------


# ------------------ Client Check In ------------------

