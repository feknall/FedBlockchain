from fl.controlpanel.fl_admin_control_panel import FlAdminControlPanel
from fl.flevents import event_listener
from fl.flevents.event_processor import FlAdminEventProcessor
from fl.rest.gateway_rest_api import GatewayRestApi

gateway_rest_api = GatewayRestApi('http://localhost:8083')
websocket_address = 'ws://localhost:8083'

control_panel = FlAdminControlPanel(gateway_rest_api)
personal_info_1, personal_info_2 = control_panel.get_personal_info()
client_index = 1

event_processor = FlAdminEventProcessor(client_id_1=personal_info_1.clientId,
                                        client_id_2=personal_info_2.clientId,
                                        client_index=client_index,
                                        gateway_rest_api=gateway_rest_api)

event_listener = event_listener.listen(event_processor, websocket_address)

control_panel.has_fl_admin_attribute()
control_panel.get_personal_info()
control_panel.create_model_metadata()
control_panel.start_training()
