import asyncio
import json
import pickle

import numpy as np
import websockets

from fl import flcommon
from fl import mnist_common
from fl.config import ClientConfig
from info_pb2 import Event
from rest import gateway_rest_api
from rest.dto import ModelMetadata, ModelSecret, TrainerMetadata

WEBSOCKET_ADDRESS = 'ws://localhost:8080'

ALL_SECRETS_RECEIVED_EVENT = "ALL_SECRETS_RECEIVED_EVENT"
AGGREGATION_FINISHED_EVENT = "AGGREGATION_FINISHED_EVENT"
ROUND_FINISHED_EVENT = "ROUND_FINISHED_EVENT"
ROUND_AND_TRAINING_FINISHED_EVENT = "ROUND_AND_TRAINING_FINISHED_EVENT"
MODEL_SECRET_ADDED_EVENT = "MODEL_SECRET_ADDED_EVENT"
CREATE_MODEL_METADATA_EVENT = "CREATE_MODEL_METADATA_EVENT"
START_TRAINING_EVENT = "START_TRAINING_EVENT"
CLIENT_SELECTED_FOR_ROUND_EVENT = "CLIENT_SELECTED_FOR_ROUND_EVENT"

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

    def __init__(self, client_id_1, client_id_2, client_index):
        self.clientId1 = client_id_1
        self.clientId2 = client_id_2
        self.clientIndex = client_index

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
        print(f"A model is created. modelId: {metadata.modelId}")

        self.modelId = metadata.modelId
        self.secretsPerClient = metadata.secretsPerClient
        self.trainingRounds = metadata.trainingRounds

    def start_training_event(self, event_payload):
        # Client
        x = json.load(event_payload)
        metadata = ModelMetadata(**x)
        print(f"A model training started. modelId: {metadata.modelId}")

    def client_selected_for_round_event(self, event_payload):
        x = json.load(event_payload)
        metadata = TrainerMetadata(**x)
        print(f"A client is selected for training. clientId: {metadata.clientId}")

        if metadata.clientId != self.clientId1 and metadata.clientId != self.clientId2:
            print("Ignoring...")
            return

        self.roundSelectedFor = metadata.roundSelectedFor

        print(f"Start training...")

        x_train, y_train = client_datasets[self.clientIndex][0], client_datasets[self.clientIndex][1]
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

        weights1 = pickle.dumps(all_servers[0])
        weights2 = pickle.dumps(all_servers[1])

        model_secret = ModelSecret(self.modelId, self.roundSelectedFor, weights1, weights2)
        gateway_rest_api.add_model_secret(model_secret)

        print("Secrets are sent.")

        print(f"Round {self.roundSelectedFor} completed.")
        print("Waiting...")


personal_info_1, personal_info_2 = gateway_rest_api.get_personal_info()
client_index = "1"
processor = EventProcessor(personal_info_1.clientId, personal_info_2.clientId, client_index)

# ------------------ Client Check In ------------------


async def periodic():
    while True:
        print('Checking-in...')
        gateway_rest_api.check_in_trainer()
        await asyncio.sleep(30)

loop = asyncio.get_event_loop()
task = loop.create_task(periodic())
try:
    loop.run_forever()
except Exception as e:
    print("Something went wrong", repr(e))


# ------------------ Client Check In ------------------


async def process_socket_events():
    async with websockets.connect(WEBSOCKET_ADDRESS) as websocket:
        async for message in websocket:
            event = Event()
            event.ParseFromString(message)
            print(event)
            event_name = event.name
            event_payload = event.payload
            if event_name == ALL_SECRETS_RECEIVED_EVENT:
                processor.all_secrets_received(event_payload)
            elif event_name == AGGREGATION_FINISHED_EVENT:
                processor.aggregation_finished(event_payload)
            elif event_name == ROUND_FINISHED_EVENT:
                processor.round_finished(event_payload)
            elif event_name == ROUND_AND_TRAINING_FINISHED_EVENT:
                processor.round_and_training_finished(event_payload)
            elif event_name == MODEL_SECRET_ADDED_EVENT:
                processor.model_secret_added(event_payload)
            elif event_name == CREATE_MODEL_METADATA_EVENT:
                processor.create_model_metadata(event_payload)
            elif event_name == START_TRAINING_EVENT:
                processor.start_training_event(event_payload)
            elif event_name == CLIENT_SELECTED_FOR_ROUND_EVENT:
                processor.client_selected_for_round_event(event_payload)


asyncio.run(process_socket_events())
