from django.urls import path
from .views import send_message

urlpatterns = [
    path("messages/", send_message, name="messages-list"),
]
