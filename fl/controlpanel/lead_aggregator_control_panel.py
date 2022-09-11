from fl.controlpanel.control_panel import ControlPanel


class LeadAggregatorControlPanel(ControlPanel):

    def check_in_func(self):
        self.gateway_rest_api.check_in_lead_aggregator()

