import sys

from fl.trainer import trainer_event_listener
from fl.trainer.trainer_control_panel import TrainerControlPanel
from fl.trainer.trainer_event_processor import TrainerEventProcessor
from fl.trainer.trainer_gateway_rest_api import TrainerGatewayRestApi


def start(address: str, port: str, client_index: int):
    gateway_rest_api = TrainerGatewayRestApi(f'http://{address}:{port}')
    websocket_address = f'ws://{address}:{port}'

    event_processor = TrainerEventProcessor(client_index=client_index, gateway_rest_api=gateway_rest_api)
    trainer_event_listener.listen(event_processor, websocket_address)

    control_panel = TrainerControlPanel(gateway_rest_api)
    control_panel.check_in()
    control_panel.has_trainer_attribute()
    control_panel.get_personal_info()


if __name__ == "__main__":
    # trainer_runner.py [address] [port] [client-index]
    # trainer_runner.py localhost 8080 1
    address = sys.argv[1]
    port = sys.argv[2]
    client_index = sys.argv[3]
    start(address, port, int(client_index))
