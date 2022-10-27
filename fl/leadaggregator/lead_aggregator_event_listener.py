import asyncio
import threading

import websockets

from fl.leadaggregator.lead_aggregator_event_processor import LeadAggregatorEventProcessor
from identity.base.support.utils import log_msg
from info_pb2 import Event

AGGREGATION_FINISHED_EVENT = "AGGREGATION_FINISHED_EVENT"
ROUND_FINISHED_EVENT = "ROUND_FINISHED_EVENT"
TRAINING_FINISHED_EVENT = "TRAINING_FINISHED_EVENT"
MODEL_SECRET_ADDED_EVENT = "MODEL_SECRET_ADDED_EVENT"
CREATE_MODEL_METADATA_EVENT = "CREATE_MODEL_METADATA_EVENT"
START_TRAINING_EVENT = "START_TRAINING_EVENT"
ENOUGH_CLIENTS_CHECKED_IN_EVENT = "ENOUGH_CLIENTS_CHECKED_IN_EVENT"
AGGREGATED_SECRET_ADDED_EVENT = "AGGREGATED_SECRET_ADDED_EVENT"


async def process_socket_events(lead_aggregator: LeadAggregatorEventProcessor, websocket_address):
    log_msg("Start listening to events...")
    async with websockets.connect(websocket_address) as websocket:
        async for message in websocket:
            event = Event()
            event.ParseFromString(message)
            print(event)
            event_name = event.name
            event_payload = event.payload
            if event_name == AGGREGATED_SECRET_ADDED_EVENT:
                lead_aggregator.aggregated_secret_added_event(event_payload)
            elif event_name == START_TRAINING_EVENT:
                lead_aggregator.start_training_event(event_payload)


def run(lead_aggregator: LeadAggregatorEventProcessor, websocket_address):
    asyncio.run(process_socket_events(lead_aggregator, websocket_address))


def listen(lead_aggregator: LeadAggregatorEventProcessor, websocket_address):
    thread = threading.Thread(target=run, args=(lead_aggregator, websocket_address))
    thread.start()
