import sys

from fl.aggregator.aggregator_event_processor import AggregatorEventProcessor
from fl.aggregator.aggregator_gateway_rest_api import AggregatorGatewayRestApi
from fl.aggregator.aggregator_control_panel import AggregatorControlPanel
from fl.flevents import event_listener



def run(address: str, port: str):
    gateway_rest_api = AggregatorGatewayRestApi(f'http://{address}:{port}')
    websocket_address = f'ws://{address}:{port}'

    event_processor = AggregatorEventProcessor(gateway_rest_api=gateway_rest_api)
    event_listener.listen(event_processor, websocket_address)

    control_panel = AggregatorControlPanel(gateway_rest_api)
    control_panel.check_in()
    control_panel.has_trainer_attribute()
    control_panel.get_personal_info()


if __name__ == "__main__":
    # aggregator_panel.py [address] [port]
    # aggregator_panel.py localhost 8091
    address = sys.argv[1]
    port = sys.argv[2]
    run(address, port)
