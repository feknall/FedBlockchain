import json
import time

import requests

from fl.dto import EndRoundModel, AggregatedSecret, \
    AggregatedSecretList
from fl.gateway_rest_api import GatewayRestApi
from identity.base.support.utils import log_msg


class LeadAggregatorGatewayRestApi(GatewayRestApi):

    def get_personal_info(self):
        req_addr = self.base_url + '/leadAggregator/getPersonalInfo'
        return self.get_personal_info_single(req_addr)

    def check_all_aggregated_secrets_received(self, model_id: str):
        log_msg("Check all aggregated secrets received...")
        log_msg("Waiting 5 seconds for stupid reasons :)")
        time.sleep(5)

        req_addr = self.base_url + '/leadAggregator/checkAllAggregatedSecretsReceived'
        log_msg(f"Request address: {req_addr}")

        params = {
            'modelId': model_id
        }

        resp = requests.get(req_addr, params=params)
        content = resp.content.decode()
        log_msg(f"Response: {content}")

        if content == "true":
            return True
        else:
            return False

    def add_end_round_model(self, body: EndRoundModel):
        log_msg("Waiting 5 seconds for stupid reasons :)")
        time.sleep(5)
        log_msg("Add end round model...")

        response = requests.post(self.base_url + '/leadAggregator/addEndRoundModel', json=body.to_map())
        log_msg(response)

    def get_aggregated_secrets_for_current_round(self, model_id: str):
        log_msg("Waiting 5 seconds for stupid reasons :)")
        time.sleep(5)
        log_msg("Sending get aggregated secrets for current round...")

        req_addr = self.base_url + '/leadAggregator/getAggregatedSecretListForCurrentRound'
        log_msg(f"Request address: {req_addr}")

        params = {
            'modelId': model_id,
        }

        resp = requests.get(req_addr, params=params)
        log_msg(resp)
        content = resp.content.decode()
        aggregated_secret_list = AggregatedSecretList(**json.loads(content))

        my_list = []
        for item in aggregated_secret_list.aggregatedSecretList:
            aggregated_secret = AggregatedSecret(**item)
            log_msg("Has weight? YES" if aggregated_secret.weights is not None else "Has weight? NO")
            log_msg(f"Model Id: {aggregated_secret.modelId}")
            my_list.append(aggregated_secret)
        return my_list

    def check_in_lead_aggregator(self):
        response = requests.post(self.base_url + '/leadAggregator/checkInLeadAggregator')
        log_msg(response)
