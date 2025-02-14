# routing.py
from django.urls import re_path
from messaging import consumers

websocket_urlpatterns = [
    re_path(r"^ws/chat_request/$", consumers.ChatRequestConsumer.as_asgi()),
]



