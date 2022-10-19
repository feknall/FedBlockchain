import json
import time

import requests

from fl.dto import ModelSecretResponse, AggregatedSecret, \
    ModelSecretList
from fl.gateway_rest_api import GatewayRestApi
from identity.base.support.utils import log_msg


class AggregatorGatewayRestApi(GatewayRestApi):

    def add_aggregated_secret(self, body: AggregatedSecret):
        log_msg("Adding aggregated secret...")

        req_addr = self.base_url + '/aggregator/addAggregatedSecret'
        log_msg(f"Request address: {req_addr}")

        response = requests.post(req_addr, json=body.to_map())
        print(response)

    def get_model_secrets_for_current_round(self, model_id: str) -> list[ModelSecretResponse]:
        log_msg("Waiting 5 seconds for stupid reasons :)")
        time.sleep(5)
        log_msg("Sending reading model secrets for current round...")

        req_addr = self.base_url + '/aggregator/getModelSecretListForCurrentRound'
        log_msg(f"Request address: {req_addr}")

        params = {
            'modelId': model_id
        }
        log_msg(f"Request params: {params}")

        resp = requests.get(req_addr, params=params)
        log_msg(resp)
        content = resp.content.decode()
        model_secret_list = ModelSecretList(**json.loads(content))

        my_list = []
        for item in model_secret_list.modelSecretList:
            secret = ModelSecretResponse(**item)
            log_msg("Has weight? YES" if secret.weights is not None else "Has weight? NO")
            log_msg(f"Model Id: {secret.modelId}")
            my_list.append(secret)
        return my_list

    def read_model_secrets(self, model_id: str):
        params = {
            'modelId': model_id,
            'round': round
        }
        response = requests.get(self.base_url + '/aggregator/getModelSecretList', params=params)
        print(response)

    def check_in_aggregator(self):
        response = requests.post(self.base_url + '/aggregator/checkInAggregator')
        log_msg(response)

    def check_all_secrets_received(self, model_id: str):
        log_msg("Check all secrets received...")
        log_msg("Waiting 5 seconds for stupid reasons :)")
        time.sleep(5)

        req_addr = self.base_url + '/aggregator/checkAllSecretsReceived'
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

    def get_personal_info_fl_admin(self):
        req_addr = self.base_url + '/aggregator/getPersonalInfo'
        return self.get_personal_info_single(req_addr)