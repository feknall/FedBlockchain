from fl.simple_periodic import SimplePeriodic
from fl.leadaggregator.lead_aggregator_gateway_rest_api import LeadAggregatorGatewayRestApi


class LeadAggregatorControlPanel(SimplePeriodic):

    def __init__(self, gateway_rest_api: LeadAggregatorGatewayRestApi):
        self.gateway_rest_api = gateway_rest_api

    def check_in_func(self):
        self.gateway_rest_api.check_in()

    def check_has_lead_aggregator_attribute(self):
        self.gateway_rest_api.check_has_lead_aggregator_attribute()

    def get_personal_info(self):
        self.gateway_rest_api.get_personal_info()
