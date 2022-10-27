import json

import requests

from fl.dto import ModelMetadata, EndRoundModel
from fl.gateway_rest_api import GatewayRestApi
from identity.base.support.utils import log_json, log_msg


class FlAdminGatewayRestApi(GatewayRestApi):

    def get_end_round_model(self, model_id: str) -> EndRoundModel:
        req_addr = self.base_url + '/flAdmin/getEndRoundModel'
        return super().get_end_round_model_base(model_id, req_addr)

    def init_ledger(self):
        response = requests.get(self.base_url + '/flAdmin/initLedger')
        print(response)

    def create_model_metadata(self, body: ModelMetadata):
        log_msg("Sending creating a model metadata...")
        log_msg("Request /flAdmin/createModelMetadata:")

        json_body = body.to_map()
        log_json(json_body)

        resp = requests.post(self.base_url + '/flAdmin/createModelMetadata', json=json_body)
        content = resp.content
        metadata = json.loads(content)

        log_msg("Response:")
        log_json(metadata)

    def start_training(self, model_id: str):
        log_msg("Sending start training...")

        req_addr = self.base_url + '/flAdmin/startTraining'
        log_msg(f"Request address: {req_addr}")

        params = {
            'modelId': model_id
        }
        log_json(params)

        resp = requests.post(req_addr, params=params)
        content = resp.content
        metadata = json.loads(content)

        log_msg("Response:")
        log_json(metadata)

    def get_personal_info_fl_admin(self):
        req_addr = self.base_url + '/flAdmin/getPersonalInfo'
        return self.get_personal_info_single(req_addr)

    def check_has_fl_admin_attribute(self):
        log_msg('Checking user has fl admin attribute ...')

        req_addr = self.base_url + '/general/checkHasFlAdminAttribute'
        log_msg(f"Request address: {req_addr}")

        response = requests.get(req_addr)
        content = response.content

        log_msg(f"Response: {content}")

        return content
