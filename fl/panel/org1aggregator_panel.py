from fl.controlpanel.aggregator_control_panel import AggregatorControlPanel
from fl.flevents import event_listener
from fl.flevents.event_processor import AggregatorEventProcessor
from fl.rest.gateway_rest_api import GatewayRestApi

gateway_rest_api = GatewayRestApi('http://localhost:8091')
websocket_address = 'ws://localhost:8091'

control_panel = AggregatorControlPanel(gateway_rest_api)
personal_info_1, personal_info_2 = control_panel.get_personal_info()
client_index = 1

event_processor = AggregatorEventProcessor(client_id_1=personal_info_1.clientId,
                                           client_id_2=personal_info_2.clientId,
                                           client_index=client_index,
                                           gateway_rest_api=gateway_rest_api)

event_listener = event_listener.listen(event_processor, websocket_address)

control_panel.check_in()
control_panel.has_trainer_attribute()
control_panel.get_personal_info()
