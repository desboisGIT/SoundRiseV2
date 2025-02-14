from django.db import models
from core.models import CustomUser
# Create your models here.

class Conversation(models.Model):
    participants = models.ManyToManyField(CustomUser, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id} entre {', '.join(user.username for user in self.participants.all())}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} → {self.receiver}: {self.content[:30]}"
    
    class Meta:
        ordering = ["-timestamp"]


class ConversationRequest(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_requests")
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_requests")
    status = models.CharField(max_length=10, choices=[("pending", "Pending"), ("accepted", "Accepted"), ("declined", "Declined")], default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Demande de {self.sender} à {self.receiver} - {self.status}"