import base64
import json

import requests

from fl.dto import PersonalInfo
from fl.dto import ModelSecretRequest
from fl.gateway_rest_api import GatewayRestApi
from identity.base.support.utils import log_msg, log_json


class TrainerGatewayRestApi(GatewayRestApi):

    def add_model_secret(self, body: ModelSecretRequest):
        response = requests.post(self.base_url + '/trainer/addModelSecret', json=body.to_map())
        print(response)

    def check_in_trainer(self):
        response = requests.post(self.base_url + '/trainer/checkInTrainer')
        log_msg(response)

    def get_personal_info_trainer(self):
        log_msg("Getting personal info...")

        req_addr = self.base_url + '/trainer/getPersonalInfo'
        log_msg(f"Request address: {req_addr}")

        resp = requests.get(req_addr)
        content = resp.content.decode()
        a_list = json.loads(content)

        personal_info_str_1 = json.loads(base64.b64decode(a_list[0]))
        log_json(personal_info_str_1)

        personal_info_1 = PersonalInfo(**personal_info_str_1)

        personal_info_str_2 = json.loads(base64.b64decode(a_list[1]))
        log_json(personal_info_str_2)

        personal_info_2 = PersonalInfo(**personal_info_str_2)

        return personal_info_1, personal_info_2
