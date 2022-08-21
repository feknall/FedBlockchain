
class ModelMetadata:
    modelId = None
    name = None
    clientsPerRound = None
    secretsPerClient = None
    status = None
    trainingRounds = None

    def __init__(self, modelId, name, clientsPerRound, secretsPerClient, status, trainingRounds):
        self.modelId = modelId
        self.name = name
        self.clients_per_round = clientsPerRound
        self.secrets_per_client = secretsPerClient
        self.status = status
        self.training_rounds = trainingRounds

    def to_map(self):
        return self.__dict__


class EndRoundModel:
    modelId = None
    round = None
    weights = None

    def __init__(self, modelId, round, weights):
        self.modelId = modelId
        self.round = round
        self.weights = weights

    def to_map(self):
        return self.__dict__


class ModelSecret:
    modelId = None
    round = None
    weights = None

    def __init__(self, modelId, round, weights):
        self.model_id = modelId
        self.round = round
        self.weights = weights

    def to_map(self):
        return self.__dict__


class AggregatedSecret:
    modelId = None
    round = None
    weights = None

    def __init__(self, modelId, round, weights):
        self.modelId = modelId
        self.round = round
        self.weights = weights

    def to_map(self):
        return self.__dict__


class PersonalInfo:
    role = None

    def __init__(self, role):
        self.role = role

    def to_map(self):
        return self.__dict__