from django.urls import re_path
from .consumers import ChatConsumer, InvitationConsumer

websocket_urlpatterns = [
    re_path(r"ws/invitations/(?P<user_id>\d+)/$", InvitationConsumer.as_asgi()),
    re_path(r"ws/chat/(?P<conversation_id>\d+)/$", ChatConsumer.as_asgi()),
]
