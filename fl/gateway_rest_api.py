import json
import time

import requests

from identity.base.support.utils import log_msg
from fl.dto import EndRoundModel, PersonalInfo


class GatewayRestApi:
    base_url = None

    def __init__(self, base_url):
        self.base_url = base_url

    def get_end_round_model_base(self, model_id: str, req_addr) -> EndRoundModel:
        log_msg("Getting end round model...")
        log_msg("Waiting 5 seconds for stupid reasons :)")
        time.sleep(5)

        log_msg(f"Request address: {req_addr}")

        params = {
            'modelId': model_id,
        }

        resp = requests.get(req_addr, params=params)
        log_msg(resp)
        content = resp.content.decode()
        end_round_model = EndRoundModel(**json.loads(content))

        log_msg("Has weight? YES" if end_round_model.weights is not None else "Has weight? NO")
        log_msg(f"Model Id: {end_round_model.modelId}")

        return end_round_model

    def get_selected_trainers_for_current_round(self):
        log_msg("Get selected trainers for current round...")
        log_msg("Request")

        resp = requests.get(self.base_url + '/general/getSelectedTrainersForCurrentRound')

    def get_personal_info_single(self, req_addr):
        log_msg("Getting personal info...")
        log_msg(f"Request address: {req_addr}")

        resp = requests.get(req_addr)
        content = resp.content.decode()
        personal_info_str_1 = json.loads(content)

        personal_info_1 = PersonalInfo(**personal_info_str_1)

        return personal_info_1

    def get_trained_model(self, model_id: str):
        params = {
            'model_id': model_id
        }
        response = requests.get(self.base_url + '/general/getTrainedModel', params=params)
        print(response)

    def check_has_aggregator_attribute(self):
        log_msg('Checking user has trainer attribute ...')

        req_addr = self.base_url + '/general/checkHasAggregatorAttribute'
        log_msg(f"Request address: {req_addr}")

        response = requests.get(req_addr)
        content = response.content.decode()

        log_msg(f"Response: {content}")

        return content

    def check_has_lead_aggregator_attribute(self):
        log_msg('Checking user has lead aggregator attribute ...')

        req_addr = self.base_url + '/general/checkHasLeadAggregatorAttribute'
        log_msg(f"Request address: {req_addr}")

        response = requests.get(req_addr)
        content = response.content.decode()

        log_msg(f"Response: {content}")

        return content

    def check_has_trainer_attribute(self):
        log_msg('Checking user has trainer attribute ...')

        req_addr = self.base_url + '/general/checkHasTrainerAttribute'
        log_msg(f"Request address: {req_addr}")

        response = requests.get(req_addr)
        content = response.content.decode()

        log_msg(f"Response: {content}")

        return content

    def check_i_am_selected_for_round(self):
        log_msg("Get I am selected for round...")

        req_addr = self.base_url + '/general/checkIAmSelectedForRound'
        log_msg(f"Request address: {req_addr}")

        resp = requests.get(req_addr)
        content = resp.content.decode()
        log_msg(f"Response: {content}")

        if content == "true":
            return True
        else:
            return False


