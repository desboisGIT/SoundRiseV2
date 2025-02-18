import json
from channels.generic.websocket import AsyncWebsocketConsumer
from core.models import CustomUser
from channels.db import database_sync_to_async
from .models import DraftBeat, CollaborationInvite
from django.db import close_old_connections
from asgiref.sync import sync_to_async


class CollaborationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """ Connexion WebSocket """
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.room_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.room_name, self.channel_name)
            await self.accept()
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
                await self.send(json.dumps({"error": "Action invalide"}))

        except json.JSONDecodeError:
            await self.send(json.dumps({"error": "Format JSON invalide"}))

    @database_sync_to_async
    def get_user(self, user_id):
        """ Récupérer un utilisateur de manière asynchrone """
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return None

    @database_sync_to_async
    def get_draftbeat(self, draftbeat_id):
        """ Récupérer un DraftBeat de manière asynchrone """
        try:
            return DraftBeat.objects.get(id=draftbeat_id)
        except DraftBeat.DoesNotExist:
            return None

    @database_sync_to_async
    def create_invite(self, sender, recipient, draftbeat):
        """ Créer une invitation """
        return CollaborationInvite.objects.create(sender=sender, recipient=recipient, draftbeat=draftbeat)

    @database_sync_to_async
    def get_invite(self, invite_id, recipient):
        """ Récupérer une invitation """
        try:
            return CollaborationInvite.objects.get(id=invite_id, recipient=recipient, status="pending")
        except CollaborationInvite.DoesNotExist:
            return None

    @database_sync_to_async
    def update_invite_status(self, invite_id, status):
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
        """ Vérifier si une invitation existe déjà """
        return CollaborationInvite.objects.filter(draftbeat=draftbeat, recipient=recipient, status="pending").exists()

    @database_sync_to_async
    def get_invites_for_draftbeat(self, draftbeat):
        """ Récupérer toutes les invitations pour un DraftBeat """
        return list(CollaborationInvite.objects.filter(draftbeat=draftbeat))

    async def send_invite(self, data):
        """ Envoyer une invitation """
        recipient_id = data.get("recipient_id")
        draftbeat_id = data.get("draftbeat_id")

        recipient = await self.get_user(recipient_id)
        draftbeat = await self.get_draftbeat(draftbeat_id)

        if not recipient:
            return await self.send(json.dumps({"error": "Utilisateur introuvable"}))

        if not draftbeat:
            return await self.send(json.dumps({"error": "DraftBeat introuvable"}))

        if draftbeat.user_id != self.user.id:
            return await self.send(json.dumps({"error": "Vous n'êtes pas le propriétaire de ce DraftBeat"}))

        if recipient.id == self.user.id:
            return await self.send(json.dumps({"error": "Vous ne pouvez pas vous inviter vous-même"}))

        if await self.invite_exists(draftbeat, recipient):
            return await self.send(json.dumps({"error": "Invitation déjà envoyée"}))

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
        await self.send(json.dumps({"success": "Invitation envoyée"}))

    from asgiref.sync import sync_to_async

    async def accept_invite(self, data):
        """ Accepter une invitation """
        invite_id = data.get("invite_id")

        # Récupérer l'invitation de manière synchrone
        invite = await sync_to_async(lambda: CollaborationInvite.objects.select_related("draftbeat", "sender").filter(id=invite_id, recipient=self.user).first())()

        if not invite:
            return await self.send(json.dumps({"error": "Invitation introuvable"}))

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

        # Envoi d'une confirmation à l'utilisateur
        await self.send(json.dumps({"success": "Invitation acceptée"}))


    async def refuse_invite(self, data):
        """ Refuser une invitation """
        invite_id = data.get("invite_id")

        # Récupérer l'invitation en mode synchrone
        invite = await sync_to_async(lambda: CollaborationInvite.objects.select_related("sender").filter(id=invite_id, recipient=self.user).first())()

        if not invite:
            return await self.send(json.dumps({"error": "Invitation introuvable"}))

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

        # Confirmation côté utilisateur
        await self.send(json.dumps({"success": "Invitation refusée"}))




    async def get_invite_status(self, data):
        """ Récupérer le statut des invitations pour un DraftBeat """
        draftbeat_id = data.get("draftbeat_id")

        draftbeat = await self.get_draftbeat(draftbeat_id)  # Supposé asynchrone
        if not draftbeat:
            return await self.send(json.dumps({"error": "DraftBeat introuvable"}))

        invites = await self.get_invites_for_draftbeat(draftbeat)  # Maintenant bien géré en async

        invite_status_list = [
            {
                "invite_id": i.id, 
                "recipient": i.recipient.username,  # Cette ligne risque d'être bloquante
                "status": i.status
            } 
            for i in invites
        ]

        await self.send(json.dumps({"invite_status": invite_status_list}))

    async def invitation_notification(self, event):
        """ Notification WebSocket pour les invitations """
        await self.send(json.dumps(event))

    async def invitation_status(self, event):
        """ Notification WebSocket pour le statut des invitations """
        await self.send(json.dumps(event))
