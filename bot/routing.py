from . import consumers
from channels.routing import route

# channel_routing = {
#     'websocket.connect': consumers.ws_connect,
#     'websocket.receive': consumers.ws_receive,
#     'websocket.disconnect': consumers.ws_disconnect
# }

channel_routing = [
	route('websocket.connect', consumers.ws_connect),
	route('websocket.receive', consumers.ws_receive),
	route('websocket.disconnect', consumers.ws_disconnect)
]