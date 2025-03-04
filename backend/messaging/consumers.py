# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async



class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the conversation ID from the URL parameters (this is now conversation_id, not room_name)
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.user = self.scope['user']  # Vous pouvez l'utiliser ensuite
        # Generate the room group name based on the conversation ID
        self.room_group_name = f'chat_{self.conversation_id}'

        # Get the conversation and its messages asynchronously
        conversation = await self.get_conversation(self.conversation_id)
        messages = await self.get_messages(self.conversation_id)

        # Accept the WebSocket connection
        await self.accept()

        # Send the initial messages to the WebSocket client
        await self.send(text_data=json.dumps({
        'messages': messages,
        }, ensure_ascii=False))  # Empêche l'échappement des caractères spéciaux


        # Join the room group (this allows the server to send messages to this room)
        await self.channel_layer.group_add(
            f'user_{self.user.id}',  # L'utilisateur doit être ajouté au groupe correspondant à son ID
            self.channel_name
        )


    async def disconnect(self, close_code):
        """Déconnecte l'utilisateur du WebSocket et quitte le groupe utilisateur."""
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "send_message":
            conversation_id = data["conversation_id"]
            receiver_id = data["receiver_id"]
            content = data["content"]

            sender = self.user
            print("send")
            # Envoyer le message
            message = await self.send_message(conversation_id, sender, receiver_id, content)
            if message is not None:
                # Marquer le message comme vu
                await self.mark_message_as_seen(message.id)

                # Envoyer la notification de message vu
                await self.channel_layer.group_send(
                    f'user_{sender.id}',  # L'expéditeur sera notifié
                    {
                        'type': 'message_seen',
                        'message_id': message.id,
                    }
                )
            else:
                print("Message is None, cannot mark as seen.")
            
    @database_sync_to_async
    def get_receiver(self, conversation, receiver_id):
        """Récupérer l'utilisateur destinataire de manière asynchrone"""
        return conversation.participants.get(id=receiver_id)

    @database_sync_to_async
    def get_conversation(self, conversation_id):
        from .models import Conversation  # Assuming Conversation and Message models exist
        return Conversation.objects.get(id=conversation_id)

    # Helper method to fetch the messages for a conversation asynchronously
    @database_sync_to_async
    def get_messages(self, conversation_id):
        from datetime import datetime
        from .models import Message
        messages = Message.objects.filter(conversation_id=conversation_id).values('sender__username', 'content', 'timestamp')

        # Format the 'timestamp' field as a string (ISO 8601 format)
        for message in messages:
            message['timestamp'] = message['timestamp'].isoformat()  # Convert datetime to string
        
        return list(messages)

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
    
    @database_sync_to_async
    def mark_message_as_seen(message_id):
        from .models import Message
        try:
            message = Message.objects.get(id=message_id)
            message.is_read = True
            message.save()
            return True
        except Message.DoesNotExist:
            return False

    # Notifier le récepteur lorsque le message a été vu
    async def message_seen(self, event):
        """Notifie le récepteur que le message a été vu"""
        message_id = event['message_id']
        print(f"Message {message_id} has been seen by the recipient.")
        
        # Vous pouvez envoyer un événement pour mettre à jour l'interface utilisateur en temps réel
        await self.send(text_data=json.dumps({
            'action': 'message_seen',
            'message_id': message_id
        },ensure_ascii=False)) 

    @database_sync_to_async
    def get_unseen_messages(self, user):
        from .models import Message
        # Récupérer les messages non vus pour l'utilisateur
        return Message.objects.filter(receiver=user, seen=False)

    async def send_message(self, conversation_id, sender, receiver_id, content):
        from .models import Conversation
        """Envoie un message dans une conversation existante."""
        try:
            conversation = await self.get_conversation(conversation_id)
            receiver = await self.get_receiver(conversation, receiver_id)
            message = await self.create_message(conversation, sender, receiver, content)

            if receiver_id == sender.id : 
                await self.send(text_data=json.dumps({
                    'error': 'Impossible de se parler à soi même'
                },ensure_ascii=False))
                return  # Exit early if the sender is trying to message themselves

            # Format the message for sending to the recipient
            message_data = {
                'sender': sender.username,
                'content': message.content,
                'timestamp': str(message.timestamp)
            }

            # Envoyer la notification au destinataire
            print(f"Sending message to group 'user_{receiver_id}': {message_data}")
            await self.channel_layer.group_send(
                f'user_{receiver_id}',
                {
                    'type': 'new_message',
                    'message': message_data
                }
            )
        except Conversation.DoesNotExist:
            await self.send(text_data=json.dumps({
                'error': f'Conversation {conversation_id} non trouvée.'
            },ensure_ascii=False))

    async def new_message(self, event):
        """Gère la réception d'un nouveau message et l'envoie au client WebSocket."""
        print(f"New message event: {event}")
        await self.send(text_data=json.dumps(event['message'], ensure_ascii=False))





class InvitationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_authenticated:
            self.room_group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            print(f"Utilisateur {self.user.username} connecté au canal {self.room_group_name}")

            # Récupérer et envoyer les invitations non lues
            unread_invitations = await self.get_unread_invitations(self.user)
            await self.send(json.dumps(
                {"type": "unread_invitations", "invitations": unread_invitations},
                ensure_ascii=False
            ))
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

            
            

        
        elif data.get('action') == 'accept_invitation':
            invitation_id = data.get('invitation_id')
            await self.accept_invitation(invitation_id)

        elif data.get('action') == 'decline_invitation':
            invitation_id = data.get('invitation_id')
            await self.decline_invitation(invitation_id)

    async def check_existing_invitation(self, receiver_id):
        
        """Vérifie si une invitation existe déjà pour ce destinataire."""
        from .models import Invitation  # Importe ton modèle

        existing_invitation = await database_sync_to_async(
            lambda: Invitation.objects.filter(sender=self.scope['user'], receiver_id=receiver_id, status='pending').exists()
        )()

        return existing_invitation


    async def send_invitation(self, receiver_id, invitation_id, message):
        """Envoie une invitation en direct au destinataire via WebSocket."""
        print("Envoi d'une invitation en direct...")
        
        await self.channel_layer.group_send(
            f"user_{receiver_id}",
            {
                'type': 'invitation_message',
                'message': message,
                'sender': self.user.username,
                'invitation_id': invitation_id  # On passe l'ID en paramètre
            }
        )
        
        print(f"Invitation {invitation_id} envoyée au canal user_{receiver_id}")


    async def invitation_message(self, event):
        """Reçoit et renvoie une invitation au client WebSocket."""
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'invitation_id': event['invitation_id'],  # Correction ici
        }))
        print(f"Invitation reçue et renvoyée au client : {event['message']}")

    @database_sync_to_async
    def get_unread_invitations(self, user):
        """Récupère les invitations en attente pour l'utilisateur et convertit created_at en string."""
        from .models import Invitation
        return [
            {
                "id": invitation.id,
                "sender_username": invitation.sender.username,
                "message": invitation.message,
                "created_at": invitation.created_at.isoformat() if invitation.created_at else None  # Convertit datetime → string
            }
            for invitation in Invitation.objects.filter(receiver=user, status="pending")
        ]
    
    async def create_invitation(self, receiver_id, message):
        from .models import Invitation
        from core.models import CustomUser
        """Créer une invitation dans la base de données."""
        try:
            receiver = await database_sync_to_async(CustomUser.objects.get)(id=receiver_id)
            invitation = await database_sync_to_async(Invitation.objects.create)(
                sender=self.user,
                receiver=receiver,
                message=message
            )
        
            await self.send_invitation(receiver_id,invitation.id, message)
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
                await self.send_invitation_accepted(invitation.sender.id,invitation.id)

                print("Invitation acceptée, conversation créée et notification envoyée.")
            else:
                print("Tentative d'acceptation d'une invitation non autorisée.")
        except Invitation.DoesNotExist:
            print(f"Invitation {invitation_id} non trouvée.")

    async def decline_invitation(self, invitation_id):
        from .models import Invitation  # Importe le modèle

        try:
            invitation = await database_sync_to_async(Invitation.objects.get)(id=invitation_id)
            if invitation.receiver == self.user:
                await database_sync_to_async(invitation.delete)()
                await self.send_invitation_refused(invitation.sender.id,invitation.id)
                print(f"Invitation {invitation_id} refusée par {self.user.username}")
            else:
                print(f"Tentative de refus non autorisée par {self.user.username}")
        except Invitation.DoesNotExist:
            print(f"Invitation {invitation_id} non trouvée.")


    @database_sync_to_async
    def create_conversation(self, sender, receiver):
        from .models import Conversation
        """Créer une conversation entre deux utilisateurs après acceptation de l'invitation."""
        
        # Vérifie si une conversation existe déjà entre ces deux utilisateurs
        existing_conversation = Conversation.objects.filter(
            participants=sender
        ).filter(
            participants=receiver
        ).first()

        if existing_conversation:
            print(f"Une conversation existe déjà entre {sender.username} et {receiver.username}.")
            return existing_conversation

        # Crée une nouvelle conversation uniquement si aucune n'existe
        conversation = Conversation.objects.create(
            title=f"Conversation entre {sender.username} et {receiver.username}"
        )
        conversation.participants.add(sender, receiver)

        print(f"Nouvelle conversation créée entre {sender.username} et {receiver.username}.")
        return conversation
        
    

    async def send_invitation_accepted(self, sender_id,invitation_id):
        """Notifier l'expéditeur que l'invitation a été acceptée."""
        await self.send(text_data=json.dumps({
            'message': 'Invitation acceptée.',
            'invitation_id':invitation_id,
        },ensure_ascii=False))

    async def send_invitation_accepted(self, sender_id, invitation_id):
        """Notifier l'expéditeur que l'invitation a été acceptée via WebSocket."""
        await self.channel_layer.group_send(
            f"user_{sender_id}",  # Envoie au groupe de l'expéditeur
            {
                'type': 'invitation_accepted',
                'message': 'Invitation acceptée.',
                'invitation_id': invitation_id,
                'receiver': self.user.username,  # L'utilisateur qui a accepté
            }
        )

    async def invitation_accepted(self, event):
        """Envoie une notification à l'expéditeur de l'invitation."""
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'invitation_id': event['invitation_id'],
            'receiver': event['receiver'],  # Qui a accepté l'invitation
        },ensure_ascii=False))
        print(f"Invitation {event['invitation_id']} acceptée par {event['receiver']}, notification envoyée à l'expéditeur.")


    async def invitation_refused(self, event):
        """Envoie une notification à l'expéditeur de l'invitation refusée."""
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'invitation_id': event['invitation_id'],
            'receiver': event['receiver'],  # Qui a refusé
        },ensure_ascii=False))
        print(f"Invitation {event['invitation_id']} refusée par {event['receiver']}, notification envoyée à l'expéditeur.")
