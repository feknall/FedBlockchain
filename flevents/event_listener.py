import asyncio
import threading

import websockets

from base.support.utils import log_msg
from flevents.event_processor import EventProcessor
from info_pb2 import Event

WEBSOCKET_ADDRESS = 'ws://localhost:8080'

ALL_SECRETS_RECEIVED_EVENT = "ALL_SECRETS_RECEIVED_EVENT"
AGGREGATION_FINISHED_EVENT = "AGGREGATION_FINISHED_EVENT"
ROUND_FINISHED_EVENT = "ROUND_FINISHED_EVENT"
ROUND_AND_TRAINING_FINISHED_EVENT = "ROUND_AND_TRAINING_FINISHED_EVENT"
MODEL_SECRET_ADDED_EVENT = "MODEL_SECRET_ADDED_EVENT"
CREATE_MODEL_METADATA_EVENT = "CREATE_MODEL_METADATA_EVENT"
START_TRAINING_EVENT = "START_TRAINING_EVENT"
CLIENT_SELECTED_FOR_ROUND_EVENT = "CLIENT_SELECTED_FOR_ROUND_EVENT"


async def process_socket_events(processor: EventProcessor):
    log_msg("Start listening to events...")
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


def run(processor):
    asyncio.run(process_socket_events(processor))


def listen(processor: EventProcessor):
    thread = threading.Thread(target=run, args=(processor,))
    thread.start()