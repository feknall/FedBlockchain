from fl import mnist_common
from fl.config import ClientConfig

config = ClientConfig()
client_datasets = mnist_common.load_train_dataset(config.number_of_clients, permute=True)


class EventProcessor:
    modelId = None
    secretsPerClient = None
    trainingRounds = None
    roundWeight = None
    gateway_rest_api = None

    # def all_secrets_received(self, event_payload):
    #     # Aggregator
    #     pass

    # def aggregation_finished(self, event_payload):
    #     # LeadAggregator
    #     pass

    def round_finished(self, event_payload):
        # Clients
        pass

    # def training_finished(self, event_payload):
    #     # All
    #     pass

    # def model_secret_added(self, event_payload):
    #     # Audit
    #     pass

    # def aggregated_secret_added_event(self, event_payload):
    #     pass

