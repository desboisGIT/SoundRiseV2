# routing.py

from django.urls import path
from .consumers import ChatConsumer,InvitationConsumer

websocket_urlpatterns = [
    path('ws/invitations/', InvitationConsumer.as_asgi()),
    path('ws/chat/<int:conversation_id>/', ChatConsumer.as_asgi()),
]
