# views.py
from rest_framework.response import Response
from .models import Invitation, Conversation
from .serializers import ConversationSerializer,InvitationSerializer
from rest_framework import generics, permissions

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
    
class InvitationListView(generics.ListAPIView):
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]  # Seuls les utilisateurs connectés peuvent voir leurs invitations

    def get_queryset(self):
        """Récupère les invitations où l'utilisateur est soit l'expéditeur soit le destinataire."""
        user = self.request.user
        return Invitation.objects.filter(sender=user) | Invitation.objects.filter(receiver=user)