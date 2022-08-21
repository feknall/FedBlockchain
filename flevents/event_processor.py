import asyncio
import json
import websockets
from types import SimpleNamespace
from rest.dto import ModelMetadata, ModelSecret
from info_pb2 import Event

WEBSOCKET_ADDRESS = 'ws://localhost:8080'

ALL_SECRETS_RECEIVED_EVENT = "ALL_SECRETS_RECEIVED_EVENT"
AGGREGATION_FINISHED_EVENT = "AGGREGATION_FINISHED_EVENT"
ROUND_FINISHED_EVENT = "ROUND_FINISHED_EVENT"
ROUND_AND_TRAINING_FINISHED_EVENT = "ROUND_AND_TRAINING_FINISHED_EVENT"
MODEL_SECRET_ADDED_EVENT = "MODEL_SECRET_ADDED_EVENT"
CREATE_MODEL_METADATA_EVENT = "CREATE_MODEL_METADATA_EVENT"
START_TRAINING_EVENT = "START_TRAINING_EVENT"


def all_secrets_received(event_payload):
    x = json.loads(event_payload)
    model_secret = ModelSecret(**x)
    print(model_secret.modelId)


def aggregation_finished(event_payload):
    pass


def round_finished(event_payload):
    pass


def round_and_training_finished(event_payload):
    pass


def model_secret_added(event_payload):
    pass


def create_model_metadata(event_payload):
    x = json.loads(event_payload)
    metadata = ModelMetadata(**x)
    print(metadata.modelId)


async def process_socket_events():
    async with websockets.connect(WEBSOCKET_ADDRESS) as websocket:
        async for message in websocket:
            event = Event()
            event.ParseFromString(message)
            print(event)
            event_name = event.name
            event_payload = event.payload
            if event_name == ALL_SECRETS_RECEIVED_EVENT:
                all_secrets_received(event_payload)
            elif event_name == AGGREGATION_FINISHED_EVENT:
                aggregation_finished(event_payload)
            elif event_name == ROUND_FINISHED_EVENT:
                round_finished(event_payload)
            elif event_name == ROUND_AND_TRAINING_FINISHED_EVENT:
                round_and_training_finished(event_payload)
            elif event_name == MODEL_SECRET_ADDED_EVENT:
                model_secret_added(event_payload)
            elif event_name == CREATE_MODEL_METADATA_EVENT:
                create_model_metadata(event_payload)

asyncio.run(process_socket_events())
