import json
import base64
import requests

from rest.dto import ModelSecret, ModelMetadata, EndRoundModel, AggregatedSecret, PersonalInfo
base_url = 'http://localhost:8080'


def init_ledger():
    response = requests.get(base_url + '/admin/initLedger')
    print(response)


def create_model_metadata(body: ModelMetadata):
    response = requests.post(base_url + '/admin/createModelMetadata', json=body.to_map())
    print(response)


def add_end_round_model(body: EndRoundModel):
    response = requests.post(base_url + '/leadAggregator/addEndRoundModel', json=body.to_map())
    print(response)


def read_aggregated_model_update(model_id: str, round: str):
    params = {
        'model_id': model_id,
        'round': round
    }
    response = requests.post(base_url + '/leadAggregator/readAggregatedModelUpdate', params=params)
    print(response)


def add_aggregated_secret(body: AggregatedSecret):
    response = requests.post(base_url + '/aggregator/addAggregatedSecret', json=body.to_map())
    print(response)


def read_model_secrets(model_id: str, round: str):
    params = {
        'model_id': model_id,
        'round': round
    }
    response = requests.get(base_url + '/aggregator/readModelSecrets', params=params)
    print(response)


def add_model_secret(body: ModelSecret):
    response = requests.post(base_url + '/trainer/addModelSecret', json=body.to_map())
    print(response)


def check_in_trainer():
    response = requests.post(base_url + '/trainer/checkInTrainer')
    print(response)


def read_end_round_model(model_id: str, round: str):
    params = {
        'model_id': model_id,
        'round': round
    }
    response = requests.post(base_url + '/user/readEndRoundModel', params=params)
    print(response)


def get_personal_info():
    resp = requests.get(base_url + '/general/getPersonalInfo')
    content = resp.content
    a_list = json.loads(content.decode())
    print(a_list)
    personal_info_str_1 = json.loads(base64.b64decode(a_list[0]))
    personal_info_1 = PersonalInfo(**personal_info_str_1)

    personal_info_str_2 = json.loads(base64.b64decode(a_list[1]))
    personal_info_2 = PersonalInfo(**personal_info_str_2)

    return personal_info_1, personal_info_2


def get_trained_model(model_id: str):
    params = {
        'model_id': model_id
    }
    response = requests.get(base_url + '/general/getTrainedModel', params=params)
    print(response)

