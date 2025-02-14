from django.shortcuts import render
import json
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Create your views here.
from rest_framework import generics, permissions
from .models import Message,Conversation,ConversationRequest
from .serializers import MessageSerializer,ConversationSerializer
from core.models import CustomUser
from django.contrib.auth.decorators import login_required

@login_required
def send_message(request):
    if request.method == "POST":
        sender = request.user
        receiver_id = request.POST.get("receiver_id")
        content = request.POST.get("content")

        try:
            receiver = CustomUser.objects.get(id=receiver_id)
        except CustomUser.DoesNotExist:
            return JsonResponse({"error": "Utilisateur non trouvé"}, status=404)

        message = Message.objects.create(sender=sender, receiver=receiver, content=content)

        # Notifier le destinataire en WebSocket
        channel_layer = get_channel_layer()
        room_name = f"user_{receiver.id}"
        async_to_sync(channel_layer.group_send)(
            f"chat_{room_name}",
            {
                "type": "chat_message",
                "message": content,
                "sender": sender.username,
            }
        )

        return JsonResponse({"message": "Message envoyé !"})
    


@api_view(["POST"])
def create_or_get_conversation(request):
    """Crée une conversation entre deux utilisateurs ou récupère celle existante"""
    user1 = request.user
    user2_id = request.data.get("user2_id")

    try:
        user2 = CustomUser.objects.get(id=user2_id)
    except CustomUser.DoesNotExist:
        return Response({"error": "Utilisateur non trouvé"}, status=404)

    conversation, created = Conversation.objects.get_or_create(
        id=min(user1.id, user2.id) * 1000000 + max(user1.id, user2.id)
    )
    conversation.participants.add(user1, user2)

    return Response(ConversationSerializer(conversation).data)

@api_view(["GET"])
def get_user_conversations(request):
    """Récupère toutes les conversations de l'utilisateur"""
    conversations = Conversation.objects.filter(participants=request.user)
    return Response(ConversationSerializer(conversations, many=True).data)