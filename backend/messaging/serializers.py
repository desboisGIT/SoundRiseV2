from rest_framework import serializers
from .models import Message,Conversation,Invitation

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "sender", "receiver", "content", "timestamp","is_read"]

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "participants", "messages", "created_at"]


class InvitationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source="sender.username", read_only=True)
    receiver_username = serializers.CharField(source="receiver.username", read_only=True)

    class Meta:
        model = Invitation
        fields = ['id', 'sender', 'receiver', 'sender_username', 'receiver_username', 'message', 'created_at', 'status']