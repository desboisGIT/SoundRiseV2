from django.urls import path
from .consumers import CollaborationConsumer

websocket_urlpatterns = [
    path("ws/collaboration/", CollaborationConsumer.as_asgi()),
]

