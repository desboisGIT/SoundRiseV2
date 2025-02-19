# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Invitation, Conversation
from .serializers import ConversationSerializer
from core.models import CustomUser
from rest_framework import generics, permissions


class SendInvitationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        receiver_id = request.data.get('receiver_id')
        receiver = CustomUser.objects.get(id=receiver_id)

        # Créer l'invitation
        invitation = Invitation.objects.create(sender=request.user, receiver=receiver)
        return Response({"message": "Invitation envoyée !"})

class AcceptInvitationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, invitation_id):
        invitation = Invitation.objects.get(id=invitation_id)

        if invitation.receiver != request.user:
            return Response({"error": "Non autorisé"}, status=403)

        # Accepter l'invitation et créer la conversation
        conversation = Conversation.objects.create()
        conversation.users.add(invitation.sender, invitation.receiver)
        invitation.is_accepted = True
        invitation.conversation = conversation
        invitation.save()

        return Response({"message": "Invitation acceptée !"})


class ConversationListView(generics.ListAPIView):
    """Lister toutes les conversations de l'utilisateur connecté."""
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Récupère les conversations où l'utilisateur est un participant."""
        return Conversation.objects.filter(participants=self.request.user).distinct()

    def list(self, request, *args, **kwargs):
        """Retourne la liste des conversations triées par date de création (du plus récent au plus ancien)."""
        queryset = self.get_queryset().order_by('-created_at')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)