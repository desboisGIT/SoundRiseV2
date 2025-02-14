"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import django  # ✅ Ajoute cette ligne
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from messaging.middleware import JWTAuthMiddleware
from messaging.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

django.setup()  # ✅ Ajoute cette ligne pour éviter l'erreur

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(
        AllowedHostsOriginValidator(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
