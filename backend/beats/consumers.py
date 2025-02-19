import json
from channels.generic.websocket import AsyncWebsocketConsumer

from channels.db import database_sync_to_async

from django.db import close_old_connections
from asgiref.sync import sync_to_async



class CollaborationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """ Connexion WebSocket spécifique à l'utilisateur """
        self.user = self.scope["user"]
        self.user_id = self.scope["url_route"]["kwargs"]["user_id"]

        # Vérifier que l'utilisateur est authentifié et correspond à l'ID donné dans l'URL
        if self.user.is_authenticated and str(self.user.id) == self.user_id:
            self.room_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()

             # Envoyer les notifications non lues
            unread_notifications = await self.get_unread_notifications(self.user)
            await self.send(json.dumps(
                {"type": "unread_notifications", "notifications": unread_notifications}, 
                ensure_ascii=False  # Empêche l'encodage en Unicode
            ))
        else:
            await self.close()

    async def disconnect(self, close_code):
        """ Déconnexion WebSocket """
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        """ Réception de messages WebSocket """
        try:
            data = json.loads(text_data)
            action = data.get("action")

            actions = {
                "send_invite": self.send_invite,
                "accept_invite": self.accept_invite,
                "refuse_invite": self.refuse_invite,
                "get_invite_status": self.get_invite_status,
                
            }

            if action in actions:
                await actions[action](data)
            else:
                await self.send(json.dumps({"error": "Action invalide"},ensure_ascii=False))

        except json.JSONDecodeError:
            await self.send(json.dumps({"error": "Format JSON invalide"},ensure_ascii=False))

    @database_sync_to_async
    def get_user(self, user_id):
        from core.models import CustomUser
        """ Récupérer un utilisateur de manière asynchrone """
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return None

    @database_sync_to_async
    
    def get_draftbeat(self, draftbeat_id):
        from .models import DraftBeat
        """ Récupérer un DraftBeat de manière asynchrone """
        try:
            return DraftBeat.objects.get(id=draftbeat_id)
        except DraftBeat.DoesNotExist:
            return None

    @database_sync_to_async
    def create_invite(self, sender, recipient, draftbeat):
        from .models import CollaborationInvite
        """ Créer une invitation """
        return CollaborationInvite.objects.create(sender=sender, recipient=recipient, draftbeat=draftbeat)

    @database_sync_to_async
    def get_invite(self, invite_id, recipient):
        from .models import CollaborationInvite
        """ Récupérer une invitation """
        try:
            return CollaborationInvite.objects.get(id=invite_id, recipient=recipient, status="pending")
        except CollaborationInvite.DoesNotExist:
            return None

    @database_sync_to_async
    def update_invite_status(self, invite_id, status):
        from .models import CollaborationInvite
        """ Mettre à jour le statut d'une invitation """
        try:
            invite = CollaborationInvite.objects.get(id=invite_id)
            invite.status = status
            invite.save()
            return invite
        except CollaborationInvite.DoesNotExist:
            return None

    @database_sync_to_async
    def add_collaborator(self, draftbeat_id, user_id):
        from .models import DraftBeat
        from core.models import CustomUser
        """ Ajouter un collaborateur à un DraftBeat """
        try:
            draftbeat = DraftBeat.objects.get(id=draftbeat_id)
            user = CustomUser.objects.get(id=user_id)
            draftbeat.co_artists.add(user)
            draftbeat.save()
            return True
        except (DraftBeat.DoesNotExist, CustomUser.DoesNotExist):
            return False

    @database_sync_to_async
    def invite_exists(self, draftbeat, recipient):
        from .models import CollaborationInvite
        """ Vérifier si une invitation existe déjà """
        return CollaborationInvite.objects.filter(draftbeat=draftbeat, recipient=recipient, status="pending").exists()

    @database_sync_to_async
    def serialize_invites(self, invites):
        return [
            {
                "invite_id": i.id, 
                "recipient": i.recipient.username,  
                "status": i.status
            } 
            for i in invites
        ]

    @database_sync_to_async
    def create_notification(self, user, message):
        """ Crée une notification pour l'utilisateur """
        from core.models import Notifications
        return Notifications.objects.create(user=user, message=message)
    
    @database_sync_to_async
    def get_unread_notifications(self, user):
        """ Récupère les notifications non lues et convertit timestamp en string """
        from core.models import Notifications
        return [
            {
                "id": n.id,
                "message": n.message,
                "timestamp": n.timestamp.isoformat() if n.timestamp else None  # Convertit datetime → string
            }
            for n in Notifications.objects.filter(user=user, is_read=False)
        ]



    @database_sync_to_async
    def get_invites_for_draftbeat(self, draftbeat):
        from .models import CollaborationInvite
        """ Récupérer toutes les invitations pour un DraftBeat """
        return list(CollaborationInvite.objects.filter(draftbeat=draftbeat))

    async def send_invite(self, data):
        """ Envoyer une invitation """
        recipient_id = data.get("recipient_id")
        draftbeat_id = data.get("draftbeat_id")

        recipient = await self.get_user(recipient_id)
        draftbeat = await self.get_draftbeat(draftbeat_id)

        if not recipient:
            return await self.send(json.dumps({"error": "Utilisateur introuvable"},ensure_ascii=False))

        if not draftbeat:
            return await self.send(json.dumps({"error": "DraftBeat introuvable"},ensure_ascii=False))

        if draftbeat.user_id != self.user.id:
            return await self.send(json.dumps({"error": "Vous n'êtes pas le propriétaire de ce DraftBeat"},ensure_ascii=False))

        if recipient.id == self.user.id:
            return await self.send(json.dumps({"error": "Vous ne pouvez pas vous inviter vous-même"},ensure_ascii=False))

        if await self.invite_exists(draftbeat, recipient):
            return await self.send(json.dumps({"error": "Invitation déjà envoyée"},ensure_ascii=False))

        invite = await self.create_invite(self.user, recipient, draftbeat)

        await self.channel_layer.group_send(
            f"user_{recipient.id}",
            {
                "type": "invitation_notification",
                "invite_id": invite.id,
                "draftbeat_title": draftbeat.title,
                "sender": self.user.username,
            },
        )
        await self.create_notification(
            recipient, 
            f"{self.user.username} vous a invité à collaborer sur '{draftbeat.title}'."
        )

        await self.send(json.dumps({"success": "Invitation envoyée"},ensure_ascii=False))
        
    from asgiref.sync import sync_to_async

    async def accept_invite(self, data):
        from .models import CollaborationInvite
        """ Accepter une invitation """
        user = self.scope["user"]
        invite_id = data.get("invite_id")

        # Récupérer l'invitation de manière synchrone
        invite = await sync_to_async(lambda: CollaborationInvite.objects.select_related("draftbeat", "sender").filter(id=invite_id, recipient=self.user).first())()

        if not invite:
            return await self.send(json.dumps({"error": "Invitation introuvable"},ensure_ascii=False))
        
        # Vérifier si l'utilisateur est bien le destinataire de l'invitation
        if invite.recipient_id != user.id:
            return await self.send(json.dumps({"error": "Accès refusé"},ensure_ascii=False))


        # Mise à jour du statut de l'invitation
        await sync_to_async(lambda: CollaborationInvite.objects.filter(id=invite.id).update(status="accepted"))()

        # Ajout du collaborateur de manière synchrone
        await self.add_collaborator(invite.draftbeat.id, self.user.id)

        # Envoi de la notification à l'expéditeur de l'invitation
        await self.channel_layer.group_send(
            f"user_{invite.sender.id}",
            {
                "type": "invitation_status",
                "invite_id": invite.id,
                "status": "accepted",
                "collaborator": self.user.username,
            },
        )
        await self.create_notification(
            invite.sender, 
            f"{self.user.username} a accepté votre invitation à collaborer sur '{invite.draftbeat.title}'."
        )

        # Envoi d'une confirmation à l'utilisateur
        await self.send(json.dumps({"success": "Invitation acceptée"},ensure_ascii=False))


    async def refuse_invite(self, data):
        from .models import CollaborationInvite
        """ Refuser une invitation """
        user = self.scope["user"]
        invite_id = data.get("invite_id")

        # Récupérer l'invitation en mode synchrone
        invite = await sync_to_async(lambda: CollaborationInvite.objects.select_related("sender").filter(id=invite_id, recipient=self.user).first())()

        if not invite:
            return await self.send(json.dumps({"error": "Invitation introuvable"},ensure_ascii=False))
        
        # Vérifier si l'utilisateur est bien le destinataire de l'invitation
        if invite.recipient_id != user.id:
            return await self.send(json.dumps({"error": "Accès refusé"},ensure_ascii=False))


        # Mise à jour du statut de l'invitation
        await sync_to_async(lambda: CollaborationInvite.objects.filter(id=invite.id).update(status="refused"))()

        # Récupérer l'ID de l'expéditeur
        sender_id = invite.sender.id

        # Envoyer la notification à l'expéditeur
        await self.channel_layer.group_send(
            f"user_{sender_id}",
            {
                "type": "invite_refused",
                "message": "Invitation refusée",
            },
        )

        await self.create_notification(
            invite.sender, 
            f"{self.user.username} a refusé votre invitation à collaborer sur '{invite.draftbeat.title}'."
        )


        # Confirmation côté utilisateur
        await self.send(json.dumps({"success": "Invitation refusée"},ensure_ascii=False))




    async def get_invite_status(self, data):
        """ Récupérer le statut des invitations pour un DraftBeat """
        user = self.scope["user"]
        draftbeat_id = data.get("draftbeat_id")

        draftbeat = await self.get_draftbeat(draftbeat_id)  # Supposé asynchrone
        if not draftbeat:
            return await self.send(json.dumps({"error": "DraftBeat introuvable"},ensure_ascii=False))
        
        if draftbeat.user_id != user.id:  # Comparer directement les IDs pour éviter les requêtes inutiles
            return await self.send(json.dumps({"error": "Accès refusé"},ensure_ascii=False))


        invites = await self.get_invites_for_draftbeat(draftbeat)  # Maintenant bien géré en async

        invite_status_list = await self.serialize_invites(invites)  

        await self.send(json.dumps({"invite_status": invite_status_list}),ensure_ascii=False)

    async def invitation_notification(self, event):
        """ Notification WebSocket pour les invitations """
        await self.send(json.dumps(event, ensure_ascii=False))
    async def invitation_status(self, event):
        """ Notification WebSocket pour le statut des invitations """
        await self.send(json.dumps(event, ensure_ascii=False))
