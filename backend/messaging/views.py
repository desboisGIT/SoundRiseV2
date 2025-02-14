from django.shortcuts import render
import json
from django.http import JsonResponse
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Create your views here.
from rest_framework import generics, permissions
from .models import Message
from .serializers import MessageSerializer
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