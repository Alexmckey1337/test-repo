from channels.routing import route, include

from main.consumers import ws_echo, ws_disconnect, ws_connect, poll_consumer, UserConsumer

http_routing = [
    route("http.request", poll_consumer, path=r"^/poll/$", method=r"^GET$"),
]

chat_routing = [
    route("websocket.connect", ws_connect, path=r"^/(?P<room>[a-zA-Z0-9_]+)/$"),
    route("websocket.receive", ws_echo),
    route("websocket.disconnect", ws_disconnect),
]

user_routing = [
    UserConsumer.as_route(path=r'^/(?P<user>\d+)/$'),
]

channel_routing = [
    # You can use a string import path as the first argument as well.
    include(chat_routing, path=r"^/ws/chat"),
    include(user_routing, path=r"^/ws/user"),
    include(http_routing),
]