import base64
import json
import time

import requests

from identity.base.support.utils import log_json, log_msg
from fl.rest.dto import ModelSecretRequest, ModelSecretResponse, ModelMetadata, EndRoundModel, AggregatedSecret, \
    PersonalInfo, ModelSecretList, AggregatedSecretList


class GatewayRestApi:
    base_url = None

    def __init__(self, base_url):
        self.base_url = base_url

    def init_ledger(self):
        response = requests.get(self.base_url + '/admin/initLedger')
        print(response)

    def create_model_metadata(self, body: ModelMetadata):
        log_msg("Sending creating a model metadata...")
        log_msg("Request /admin/createModelMetadata:")

        json_body = body.to_map()
        log_json(json_body)

        resp = requests.post(self.base_url + '/admin/createModelMetadata', json=json_body)
        content = resp.content
        metadata = json.loads(content)

        log_msg("Response:")
        log_json(metadata)

    def start_training(self, model_id: str):
        log_msg("Sending start training...")

        req_addr = self.base_url + '/admin/startTraining'
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

    def get_selected_trainers_for_current_round(self):
        log_msg("Get selected trainers for current round...")
        log_msg("Request")

        resp = requests.get(self.base_url + '/general/getSelectedTrainersForCurrentRound')

    def read_model_secrets(self, model_id: str):
        params = {
            'modelId': model_id,
            'round': round
        }
        response = requests.get(self.base_url + '/aggregator/getModelSecretList', params=params)
        print(response)

    def add_model_secret(self, body: ModelSecretRequest):
        response = requests.post(self.base_url + '/trainer/addModelSecret', json=body.to_map())
        print(response)

    def check_in_trainer(self):
        response = requests.post(self.base_url + '/trainer/checkInTrainer')
        log_msg(response)

    def check_in_aggregator(self):
        response = requests.post(self.base_url + '/aggregator/checkInAggregator')
        log_msg(response)

    def check_in_lead_aggregator(self):
        response = requests.post(self.base_url + '/leadAggregator/checkInLeadAggregator')
        log_msg(response)

    def get_end_round_model(self, model_id: str) -> EndRoundModel:
        log_msg("Getting end round model...")
        log_msg("Waiting 5 seconds for stupid reasons :)")
        time.sleep(5)

        req_addr = self.base_url + '/trainer/getEndRoundModel'
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

    def get_personal_info(self):
        log_msg("Getting personal info...")

        req_addr = self.base_url + '/general/getPersonalInfo'
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

    def check_has_fl_admin_attribute(self):
        log_msg('Checking user has fl admin attribute ...')

        req_addr = self.base_url + '/general/checkHasFlAdminAttribute'
        log_msg(f"Request address: {req_addr}")

        response = requests.get(req_addr)
        content = response.content

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
