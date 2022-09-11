import asyncio
import threading

from identity.base.support.utils import log_msg
from fl.rest.gateway_rest_api import GatewayRestApi


class ControlPanel:
    modelId = None
    gateway_rest_api = None

    def __init__(self, gateway_rest_api: GatewayRestApi):
        self.gateway_rest_api = gateway_rest_api

    def get_personal_info(self):
        return self.gateway_rest_api.get_personal_info()

    def create_model_metadata(self):
        pass

    def start_training(self):
        self.gateway_rest_api.start_training(self.modelId)

    def has_trainer_attribute(self):
        self.gateway_rest_api.check_has_trainer_attribute()

    def has_fl_admin_attribute(self):
        self.gateway_rest_api.check_has_fl_admin_attribute()

    def check_in_func(self):
        pass

    async def periodic(self):
        while True:
            log_msg('Checking-in...')
            self.check_in_func()
            await asyncio.sleep(30)

    def loop_in_thread(self, loop):
        loop.create_task(self.periodic())
        try:
            loop.run_forever()
        except Exception as e:
            print("Something went wrong", repr(e))

    def check_in(self):
        loop = asyncio.new_event_loop()
        thread = threading.Thread(target=self.loop_in_thread, args=(loop,))
        thread.start()



