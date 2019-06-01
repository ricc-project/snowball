from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter


import web_socket.routing
from web_socket.middleware import MacAuthMiddleware

application = ProtocolTypeRouter({
    'websocket': MacAuthMiddleware(
        URLRouter(
            web_socket.routing.websocket_url
        )
    ),
})