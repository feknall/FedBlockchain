import sys

from fl.leadaggregator.lead_aggregator_control_panel import LeadAggregatorControlPanel
from fl.flevents import event_listener
from fl.leadaggregator.lead_aggregator_event_processor import LeadAggregatorEventProcessor

from fl.gateway_rest_api import GatewayRestApi


def run(address: str, port: str):
    gateway_rest_api = GatewayRestApi(f'http://{address}:{port}')
    websocket_address = f'ws://{address}:{port}'

    control_panel = LeadAggregatorControlPanel(gateway_rest_api)
    event_processor = LeadAggregatorEventProcessor(gateway_rest_api=gateway_rest_api)

    event_listener.listen(event_processor, websocket_address)

    control_panel.check_in()
    control_panel.has_fl_admin_attribute()
    control_panel.get_personal_info()


if __name__ == "__main__":
    # trainer_runner.py [address] [port]
    # trainer_runner.py localhost 8082
    address = sys.argv[1]
    port = sys.argv[2]
    run(address, port)
