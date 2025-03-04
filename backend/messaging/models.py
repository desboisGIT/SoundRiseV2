from django.db import models
from core.models import CustomUser
from django.core.exceptions import ValidationError
# Create your models here.

class Conversation(models.Model):
    title=models.CharField(max_length=200,default='Conversation')
    participants = models.ManyToManyField(CustomUser, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Empêche la création si une conversation existe déjà avec exactement ces deux participants."""
        if self.pk is None and self.participants.count() == 2:
            existing_conversation = Conversation.objects.filter(
                participants=self.participants.all()[0]
            ).filter(
                participants=self.participants.all()[1]
            ).exists()
            if existing_conversation:
                raise ValidationError("Une conversation existe déjà entre ces deux utilisateurs.")
        
        super().save(*args, **kwargs)

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



    
class Invitation(models.Model):
    sender = models.ForeignKey(CustomUser, related_name="sent_invitations", on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name="received_invitations", on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')  # 'pending', 'accepted', 'rejected'

    def __str__(self):
        return f"Invitation de {self.sender} à {self.receiver}"