from fl.controlpanel.control_panel import ControlPanel


class AggregatorControlPanel(ControlPanel):

    def check_in_func(self):
        self.gateway_rest_api.check_in_aggregator()
