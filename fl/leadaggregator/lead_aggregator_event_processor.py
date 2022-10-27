import base64
import json
import pickle

import numpy as np

from fl.flevents.event_processor import EventProcessor
from fl.leadaggregator.lead_aggregator_gateway_rest_api import LeadAggregatorGatewayRestApi
from fl.dto import AggregatedSecret, \
    EndRoundModel, ModelMetadata
from identity.base.support.utils import log_msg


class LeadAggregatorEventProcessor(EventProcessor):
    current_round = -1
    gateway_rest_api = None

    def __init__(self, secrets_per_client, gateway_rest_api: LeadAggregatorGatewayRestApi):
        self.gateway_rest_api = gateway_rest_api
        self.secretsPerClient = secrets_per_client

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

    def start_training_event(self, event_payload):
        x = json.loads(event_payload)
        metadata = ModelMetadata(**x)
        log_msg(f"EVENT: A model training started. modelId: {metadata.modelId}")
        self.modelId = metadata.modelId