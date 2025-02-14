import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async




class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        sender = data["sender"]

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "message": message, "sender": sender},
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({"message": event["message"], "sender": event["sender"]}))




import logging

logger = logging.getLogger(__name__)

class ChatRequestConsumer(AsyncWebsocketConsumer):
    """ Consommateur WebSocket pour les demandes de conversation """

    async def connect(self):
        token = self.scope.get('headers', {}).get('authorization', None)
        if token is None:
            # Si le token n'est pas présent, rejeter la connexion
            await self.close()
        else:
            # Extraire et valider le token ici (par exemple avec JWT)
            # Si la validation échoue, vous pouvez aussi fermer la connexion
            self.user = await self.validate_token(token)
            if self.user is None:
                await self.close()

            # Si tout est bon, accepter la connexion
            await self.accept()


    

    async def receive(self, text_data):
        """ Gère les actions reçues via WebSocket """
        data = json.loads(text_data)
        action = data.get("action")
        logger.info(f"Message reçu de {self.user.username} : {action}")

        if action == "send_request":
            await self.send_request(data)
        elif action == "accept_request":
            await self.accept_request(data)
        elif action == "decline_request":
            await self.decline_request(data)

    @database_sync_to_async
    def get_user(self, user_id):
        from core.models import CustomUser
        """ Récupère un utilisateur par son ID """
        logger.debug(f"Récupération de l'utilisateur avec l'ID {user_id}")
        return CustomUser.objects.get(id=user_id)

    async def send_request(self, data):
        from messaging.models import ConversationRequest
        """ Envoie une demande de conversation à un utilisateur """
        receiver_id = data.get("receiver_id")
        receiver = await self.get_user(receiver_id)

        logger.info(f"{self.user.username} envoie une demande à {receiver.username}")
        request, created = await database_sync_to_async(ConversationRequest.objects.get_or_create)(sender=self.user, receiver=receiver, status="pending")

        if created:
            logger.info(f"Demande de conversation créée entre {self.user.username} et {receiver.username}")
            await self.channel_layer.group_send(
                f"user_{receiver.id}",
                {
                    "type": "chat_request_notification",
                    "sender_id": self.user.id,
                    "sender_username": self.user.username,
                }
            )

    async def accept_request(self, data):
        from messaging.models import ConversationRequest, Conversation
        """ Accepte une demande de conversation et crée une conversation """
        request_id = data.get("request_id")
        request = await database_sync_to_async(ConversationRequest.objects.get)(id=request_id)

        logger.info(f"{self.user.username} accepte la demande de conversation de {request.sender.username}")
        if request.receiver == self.user:
            request.status = "accepted"
            await database_sync_to_async(request.save)()

            conversation = await database_sync_to_async(Conversation.objects.create)()
            await database_sync_to_async(conversation.participants.add)(request.sender, request.receiver)

            logger.info(f"Conversation créée entre {request.sender.username} et {request.receiver.username}")
            await self.channel_layer.group_send(
                f"user_{request.sender.id}",
                {
                    "type": "chat_request_accepted",
                    "conversation_id": conversation.id,
                }
            )

    async def decline_request(self, data):
        from messaging.models import ConversationRequest
        """ Refuse une demande de conversation """
        request_id = data.get("request_id")
        request = await database_sync_to_async(ConversationRequest.objects.get)(id=request_id)

        logger.info(f"{self.user.username} refuse la demande de conversation de {request.sender.username}")
        if request.receiver == self.user:
            request.status = "declined"
            await database_sync_to_async(request.save)()

            await self.channel_layer.group_send(
                f"user_{request.sender.id}",
                {
                    "type": "chat_request_declined",
                    "request_id": request.id,
                }
            )

    async def chat_request_notification(self, event):
        """ Envoie une notification de demande de chat """
        await self.send(text_data=json.dumps(event))

    async def chat_request_accepted(self, event):
        """ Notifie l'acceptation d'une demande de chat """
        await self.send(text_data=json.dumps(event))

    async def chat_request_declined(self, event):
        """ Notifie le refus d'une demande de chat """
        await self.send(text_data=json.dumps(event))