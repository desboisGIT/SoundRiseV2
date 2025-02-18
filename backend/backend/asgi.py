# asgi.py

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

from messaging.middleware import JWTAuthMiddleware

import messaging.routing
import beats.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        URLRouter(
            beats.routing.websocket_urlpatterns + 
            messaging.routing.websocket_urlpatterns
        )
    ),
})
