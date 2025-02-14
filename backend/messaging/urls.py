from django.urls import path
from .views import send_message,create_or_get_conversation,get_user_conversations

app_name = "messaging"
urlpatterns = [
    path("messages/", send_message, name="messages-list"),
    path("conversation/", create_or_get_conversation, name="create_or_get_conversation"),
    path("conversations/", get_user_conversations, name="get_user_conversations"),

]
