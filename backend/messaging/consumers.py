# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Connecte l'utilisateur au WebSocket et le joint à son groupe utilisateur."""
        self.user = self.scope['user']
        self.room_name = f'user_{self.user.id}'

        # Rejoindre le groupe de l'utilisateur
        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """Déconnecte l'utilisateur du WebSocket et quitte le groupe utilisateur."""
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print(f"Message reçu : {text_data}")  # Vérifie si un message est reçu
        data = json.loads(text_data)
        action = data.get("action")

        if action == "send_message":
            conversation_id = data["conversation_id"]
            receiver_id = data["receiver_id"]
            content = data["content"]

            sender = self.user

            # Envoyer le message
            await self.send_message(conversation_id, sender, receiver_id, content)
            
    @database_sync_to_async
    def get_receiver(self, conversation, receiver_id):
        """Récupérer l'utilisateur destinataire de manière asynchrone"""
        return conversation.participants.get(id=receiver_id)

    @database_sync_to_async
    def get_conversation(self, conversation_id):
        from .models import Conversation
        """Récupérer la conversation de manière asynchrone"""
        return Conversation.objects.get(id=conversation_id)

    @database_sync_to_async
    def create_message(self, conversation, sender, receiver, content):
        from .models import Message
        """Créer un message dans la base de données"""
        return Message.objects.create(
            conversation=conversation,
            sender=sender,
            receiver=receiver,
            content=content
        )

    async def send_message(self, conversation_id, sender, receiver_id, content):
        from .models import Conversation
        """Envoie un message dans une conversation existante."""
        try:
            conversation = await self.get_conversation(conversation_id)
            receiver = await self.get_receiver(conversation, receiver_id)
            message = await self.create_message(conversation, sender, receiver, content)

            # Envoyer la notification au destinataire
            await self.channel_layer.group_send(
                f'user_{receiver_id}',
                {
                    'type': 'new_message',
                    'message': {
                        'sender': sender.username,
                        'content': message.content,
                        'timestamp': str(message.timestamp)
                    }
                }
            )
        except Conversation.DoesNotExist:
            await self.send(text_data=json.dumps({
                'error': f'Conversation {conversation_id} non trouvée.'
            }))

    async def new_message(self, event):
        """Gère la réception d'un nouveau message et l'envoie au client WebSocket."""
        await self.send(text_data=json.dumps(event['message']))




class InvitationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.room_group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            print(f"Utilisateur {self.user.username} connecté au canal {self.room_group_name}")
        else:
            print("Utilisateur non authentifié - connexion refusée")
            await self.close()

    async def receive(self, text_data):
        """Cette méthode gère les messages entrants."""
        print(f"Message reçu : {text_data}")
        data = json.loads(text_data)

        # Vérifie l'action
        if data.get('action') == 'send_invitation':
            receiver_id = data.get('receiver_id')
            message = data.get('message', 'Nouvelle invitation')

            existing_invitation = await self.check_existing_invitation(receiver_id)
            
            
            if existing_invitation:
                print(f"Invitation déjà existante pour {receiver_id}, action annulée.")
                return
            
            # Crée l'invitation en base de données
            await self.create_invitation(receiver_id, message)

            # Envoie la notification au destinataire
            await self.send_invitation(receiver_id, message)
        
        elif data.get('action') == 'accept_invitation':
            invitation_id = data.get('invitation_id')
            await self.accept_invitation(invitation_id)

    async def check_existing_invitation(self, receiver_id):
        
        """Vérifie si une invitation existe déjà pour ce destinataire."""
        from .models import Invitation  # Importe ton modèle

        existing_invitation = await database_sync_to_async(
            lambda: Invitation.objects.filter(sender=self.scope['user'], receiver_id=receiver_id, status='pending').exists()
        )()

        return existing_invitation


    async def send_invitation(self, receiver_id, message):
        print("q")
        """Envoie une invitation en direct au destinataire via WebSocket."""
        await self.channel_layer.group_send(
            f"user_{receiver_id}",
            {
                'type': 'invitation_message',
                'message': message,
                'sender': self.user.username,
            }
        )
        print(f"Invitation envoyée au canal user_{receiver_id}")

    async def invitation_message(self, event):
        """Reçoit et renvoie une invitation au client WebSocket."""
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
        }))
        print(f"Invitation reçue et renvoyée au client : {event['message']}")

    @database_sync_to_async
    def create_invitation(self, receiver_id, message):
        from .models import Invitation
        from core.models import CustomUser
        """Créer une invitation dans la base de données."""
        try:
            receiver = CustomUser.objects.get(id=receiver_id)
            Invitation.objects.create(
                sender=self.user,
                receiver=receiver,
                message=message
            )
            print(f"Invitation créée en base de données pour le destinataire {receiver.username}")
        except Exception as e:
            print(f"Erreur lors de la création de l'invitation : {e}")

    async def accept_invitation(self, invitation_id):
        """Accepter une invitation, créer une conversation et notifier l'expéditeur."""
        from .models import Invitation  # Importe le modèle

        try:
            # Récupérer l'invitation de manière asynchrone
            invitation = await database_sync_to_async(Invitation.objects.select_related('receiver', 'sender').get)(id=invitation_id)

            # Vérifier que l'utilisateur est bien le destinataire de l'invitation
            if invitation.receiver == self.user:
                # Marquer l'invitation comme acceptée
                invitation.status = "accepted"
                await database_sync_to_async(invitation.save)()

                print(f"Invitation {invitation_id} acceptée par {self.user.username}")

                # Créer la conversation entre les deux utilisateurs
                await self.create_conversation(invitation.sender, invitation.receiver)

                # Notifier l'expéditeur que l'invitation a été acceptée
                await self.send_invitation_accepted(invitation.sender.id)

                print("Invitation acceptée, conversation créée et notification envoyée.")
            else:
                print("Tentative d'acceptation d'une invitation non autorisée.")
        except Invitation.DoesNotExist:
            print(f"Invitation {invitation_id} non trouvée.")

    @database_sync_to_async
    def create_conversation(self, sender, receiver):
        """Créer une conversation entre deux utilisateurs après acceptation de l'invitation."""
        from .models import Conversation  # Importe le modèle

        # Vérifie si une conversation existe déjà entre les deux utilisateurs
        conversation, created = Conversation.objects.get_or_create(
            title=f"Conversation entre {sender.username} et {receiver.username}"
        )

        # Ajoute les utilisateurs à la conversation s'ils ne sont pas déjà participants
        conversation.participants.add(sender, receiver)

        if created:
            print(f"Nouvelle conversation créée entre {sender.username} et {receiver.username}.")
        else:
            print(f"Une conversation existait déjà entre {sender.username} et {receiver.username}.")

        return conversation

    async def send_invitation_accepted(self, sender_id):
        """Notifier l'expéditeur que l'invitation a été acceptée."""
        await self.channel_layer.group_send(
            f"user_{sender_id}",
            {
                'type': 'invitation_accepted',
                'message': f"L'invitation a été acceptée par {self.user.username}.",
            }
        )