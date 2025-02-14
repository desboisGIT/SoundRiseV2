from rest_framework import serializers
from .models import Message,Conversation

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "sender", "receiver", "content", "timestamp","is_read"]

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "participants", "messages", "created_at"]
