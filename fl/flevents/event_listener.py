import asyncio
import threading

import websockets

from identity.base.support.utils import log_msg
from fl.flevents.event_processor import EventProcessor
from info_pb2 import Event


AGGREGATION_FINISHED_EVENT = "AGGREGATION_FINISHED_EVENT"
ROUND_FINISHED_EVENT = "ROUND_FINISHED_EVENT"
TRAINING_FINISHED_EVENT = "TRAINING_FINISHED_EVENT"
MODEL_SECRET_ADDED_EVENT = "MODEL_SECRET_ADDED_EVENT"
CREATE_MODEL_METADATA_EVENT = "CREATE_MODEL_METADATA_EVENT"
START_TRAINING_EVENT = "START_TRAINING_EVENT"
ENOUGH_CLIENTS_CHECKED_IN_EVENT = "ENOUGH_CLIENTS_CHECKED_IN_EVENT"
AGGREGATED_SECRET_ADDED_EVENT = "AGGREGATED_SECRET_ADDED_EVENT"


async def process_socket_events(processor: EventProcessor, websocket_address):
    log_msg("Start listening to events...")
    async with websockets.connect(websocket_address) as websocket:
        async for message in websocket:
            event = Event()
            event.ParseFromString(message)
            print(event)
            event_name = event.name
            event_payload = event.payload
            if event_name == AGGREGATION_FINISHED_EVENT:
                processor.aggregation_finished(event_payload)
            elif event_name == ROUND_FINISHED_EVENT:
                processor.round_finished(event_payload)
            elif event_name == TRAINING_FINISHED_EVENT:
                processor.training_finished(event_payload)
            elif event_name == MODEL_SECRET_ADDED_EVENT:
                processor.model_secret_added(event_payload)
            elif event_name == CREATE_MODEL_METADATA_EVENT:
                processor.create_model_metadata(event_payload)
            elif event_name == START_TRAINING_EVENT:
                processor.start_training_event(event_payload)
            elif event_name == AGGREGATED_SECRET_ADDED_EVENT:
                processor.aggregated_secret_added_event(event_payload)


def run(processor, websocket_address):
    asyncio.run(process_socket_events(processor, websocket_address))


def listen(processor: EventProcessor, websocket_address):
    thread = threading.Thread(target=run, args=(processor, websocket_address))
    thread.start()
