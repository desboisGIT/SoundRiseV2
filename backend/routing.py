from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from django.urls import path
from messaging.consumers import ChatConsumer, InvitationConsumer

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/chat/", ChatConsumer.as_asgi()),
            path("ws/invitation/", InvitationConsumer.as_asgi()),
        ])
    ),
})