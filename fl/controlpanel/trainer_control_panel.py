from fl.controlpanel.control_panel import ControlPanel


class TrainerControlPanel(ControlPanel):

    def check_in_func(self):
        self.gateway_rest_api.check_in_trainer()
