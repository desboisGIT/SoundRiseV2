from django.urls import re_path, path
from .consumers import CollaborationConsumer

websocket_urlpatterns = [
    re_path(r"ws/collaboration/(?P<user_id>\d+)/$", CollaborationConsumer.as_asgi()),
]