import requests
from dto import ModelSecret, ModelMetadata, EndRoundModel, AggregatedSecret, PersonalInfo
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
    response = requests.post(base_url + '/user/addModelSecret', json=body.to_map())
    print(response)


def read_end_round_model(model_id: str, round: str):
    params = {
        'model_id': model_id,
        'round': round
    }
    response = requests.post(base_url + '/user/readEndRoundModel', params=params)
    print(response)


def get_role_in_certificate():
    response = requests.get(base_url + '/general/getRoleInCertificate')
    print(response)


def get_trained_model(model_id: str):
    params = {
        'model_id': model_id
    }
    response = requests.get(base_url + '/general/getTrainedModel', params=params)
    print(response)
