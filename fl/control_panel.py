import asyncio
import threading
from random import randint

from base.support.utils import log_msg
from flevents.event_processor import EventProcessor
from rest.dto import ModelMetadata
from rest.gateway_rest_api import GatewayRestApi
from flevents import event_listener

class ControlPanel:
    modelId = None
    gateway_rest_api = None

    def __init__(self, gateway_rest_api):
        self.gateway_rest_api = gateway_rest_api

    def get_personal_info(self):
        return self.gateway_rest_api.get_personal_info()

    def create_model_metadata(self):
        self.modelId = str(randint(0, 1000))
        body = ModelMetadata(self.modelId, "model1", "1", "2", "2")
        self.gateway_rest_api.create_model_metadata(body)

    def start_training(self):
        self.gateway_rest_api.start_training(self.modelId)

    def has_trainer_attribute(self):
        self.gateway_rest_api.check_has_trainer_attribute()

    async def periodic(self):
        while True:
            log_msg('Checking-in...')
            self.gateway_rest_api.check_in_trainer()
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


gateway_rest_api = GatewayRestApi('http://localhost:8080')

control_panel = ControlPanel(gateway_rest_api)
personal_info_1, personal_info_2 = control_panel.get_personal_info()
client_index = 1

event_processor = EventProcessor(client_id_1=personal_info_1.clientId,
                                 client_id_2=personal_info_2.clientId,
                                 client_index=client_index,
                                 gateway_rest_api=gateway_rest_api)

event_listener = event_listener.listen(event_processor)


control_panel.check_in()
# control_panel.has_trainer_attribute()
# control_panel.get_personal_info()
# control_panel.create_model_metadata()
# control_panel.start_training()
