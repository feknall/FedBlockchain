from fl.aggregator.aggregator_gateway_rest_api import AggregatorGatewayRestApi
from fl.simple_periodic import SimplePeriodic


class AggregatorControlPanel(SimplePeriodic):

    def __init__(self, gateway_rest_api: AggregatorGatewayRestApi):
        self.gateway_rest_api = gateway_rest_api

    def check_in_func(self):
        self.gateway_rest_api.check_in_aggregator()

    def has_aggregator_attribute(self):
        self.gateway_rest_api.check_has_aggregator_attribute()

    def get_personal_info(self):
        self.gateway_rest_api.get_personal_info_aggregator()


