# import asyncio
# import threading
#
# import websockets
#
# from fl.aggregator.aggregator_event_processor import AggregatorEventProcessor
# from fl.fladmin.fl_admin_event_processor import FlAdminEventProcessor
# from fl.leadaggregator.lead_aggregator_event_processor import LeadAggregatorEventProcessor
# from fl.trainer.trainer_event_processor import TrainerEventProcessor
# from identity.base.support.utils import log_msg
# from info_pb2 import Event
#
# AGGREGATION_FINISHED_EVENT = "AGGREGATION_FINISHED_EVENT"
# ROUND_FINISHED_EVENT = "ROUND_FINISHED_EVENT"
# TRAINING_FINISHED_EVENT = "TRAINING_FINISHED_EVENT"
# MODEL_SECRET_ADDED_EVENT = "MODEL_SECRET_ADDED_EVENT"
# CREATE_MODEL_METADATA_EVENT = "CREATE_MODEL_METADATA_EVENT"
# START_TRAINING_EVENT = "START_TRAINING_EVENT"
# ENOUGH_CLIENTS_CHECKED_IN_EVENT = "ENOUGH_CLIENTS_CHECKED_IN_EVENT"
# AGGREGATED_SECRET_ADDED_EVENT = "AGGREGATED_SECRET_ADDED_EVENT"
#
#
# async def process_socket_events(lead_aggregator: LeadAggregatorEventProcessor,
#                                 trainer: TrainerEventProcessor,
#                                 fl_admin: FlAdminEventProcessor,
#                                 aggregator: AggregatorEventProcessor,
#                                 websocket_address):
#     log_msg("Start listening to events...")
#     async with websockets.connect(websocket_address) as websocket:
#         async for message in websocket:
#             event = Event()
#             event.ParseFromString(message)
#             print(event)
#             event_name = event.name
#             event_payload = event.payload
#             if event_name == AGGREGATION_FINISHED_EVENT:
#                 # processor.aggregation_finished(event_payload)
#                 pass
#             elif event_name == ROUND_FINISHED_EVENT:
#                 # processor.round_finished(event_payload)
#                 fl_admin.round_finished(event_payload)
#                 trainer.round_finished(event_payload)
#             elif event_name == TRAINING_FINISHED_EVENT:
#                 # processor.training_finished(event_payload)
#                 trainer.training_finished(event_payload)
#             elif event_name == MODEL_SECRET_ADDED_EVENT:
#                 # processor.model_secret_added(event_payload)
#                 aggregator.model_secret_added(event_payload)
#             elif event_name == CREATE_MODEL_METADATA_EVENT:
#                 # processor.create_model_metadata(event_payload)
#                 fl_admin.create_model_metadata(event_payload)
#             elif event_name == START_TRAINING_EVENT:
#                 # processor.start_training_event(event_payload)
#                 fl_admin.start_training_event(event_payload)
#                 trainer.start_training_event(event_payload)
#             elif event_name == AGGREGATED_SECRET_ADDED_EVENT:
#                 # processor.aggregated_secret_added_event(event_payload)
#                 lead_aggregator.aggregated_secret_added_event(event_payload)
#
#
# def run(lead_aggregator: LeadAggregatorEventProcessor,
#         trainer: TrainerEventProcessor,
#         fl_admin: FlAdminEventProcessor,
#         aggregator: AggregatorEventProcessor,
#         websocket_address):
#     asyncio.run(process_socket_events(lead_aggregator, trainer, fl_admin, aggregator, websocket_address))
#
#
# def listen(lead_aggregator: LeadAggregatorEventProcessor,
#            trainer: TrainerEventProcessor,
#            fl_admin: FlAdminEventProcessor,
#            aggregator: AggregatorEventProcessor,
#            websocket_address):
#     thread = threading.Thread(target=run, args=(lead_aggregator, trainer, fl_admin, aggregator, websocket_address))
#     thread.start()
