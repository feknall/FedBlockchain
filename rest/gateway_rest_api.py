import json
import base64
import requests

from base.support.utils import log_json, log_msg
from rest.dto import ModelSecret, ModelMetadata, EndRoundModel, AggregatedSecret, PersonalInfo 


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
        log_msg("Request /admin/createModelMetadata:")
    
        params = {
            'modelId': model_id
        }
        log_json(params)
    
        resp = requests.post(self.base_url + '/admin/startTraining', params=params)
        content = resp.content
        metadata = json.loads(content)
    
        log_msg("Response:")
        log_json(metadata)
    
    def add_end_round_model(self, body: EndRoundModel):
        response = requests.post(self.base_url + '/leadAggregator/addEndRoundModel', json=body.to_map())
        print(response)
    
    def read_aggregated_model_update(self, model_id: str, round: str):
        params = {
            'model_id': model_id,
            'round': round
        }
        response = requests.post(self.base_url + '/leadAggregator/readAggregatedModelUpdate', params=params)
    
    def add_aggregated_secret(self, body: AggregatedSecret):
        response = requests.post(self.base_url + '/aggregator/addAggregatedSecret', json=body.to_map())
        print(response)
    
    def read_model_secrets(self, model_id: str, round: str):
        params = {
            'model_id': model_id,
            'round': round
        }
        response = requests.get(self.base_url + '/aggregator/readModelSecrets', params=params)
        print(response)
    
    def add_model_secret(self, body: ModelSecret):
        response = requests.post(self.base_url + '/trainer/addModelSecret', json=body.to_map())
        print(response)
    
    def check_in_trainer(self):
        response = requests.post(self.base_url + '/trainer/checkInTrainer')
        log_msg(response)
    
    def read_end_round_model(self, model_id: str, round: str):
        params = {
            'model_id': model_id,
            'round': round
        }
        response = requests.post(self.base_url + '/user/readEndRoundModel', params=params)
        print(response)
    
    def get_personal_info(self):
        log_msg("Getting personal info...")
        log_msg("Request /general/getPersonalInfo:")
    
        resp = requests.get(self.base_url + '/general/getPersonalInfo')
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

        response = requests.get(self.base_url + '/general/checkHasAggregatorAttribute')
        content = response.content.decode()

        log_msg(f"Response: {content}")

        return content

    def check_has_lead_aggregator_attribute(self):
        log_msg('Checking user has lead aggregator attribute ...')

        response = requests.get(self.base_url + '/general/checkHasLeadAggregatorAttribute')
        content = response.content.decode()

        log_msg(f"Response: {content}")

        return content

    def check_has_trainer_attribute(self):
        log_msg('Checking user has trainer attribute ...')

        response = requests.get(self.base_url + '/general/checkHasTrainerAttribute')
        content = response.content.decode()

        log_msg(f"Response: {content}")

        return content

    def check_has_fl_admin_attribute(self):
        log_msg('Checking user has fl admin attribute ...')

        response = requests.get(self.base_url + '/general/checkHasFlAdminAttribute')
        content = response.content

        log_msg(f"Response: {content}")

        return content
    