from django.db import models
from core.models import CustomUser
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

class Beat(models.Model):
    """
    Modèle représentant un beat musical sur Soundrise.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="beats")  # Créateur du beat
    title = models.CharField(max_length=255)  # Titre du beat
    audio_file = models.FileField(upload_to="beats/audio/")  # Fichier audio du beat
    cover_image = models.ImageField(upload_to="beats/covers/", blank=True, null=True)  # Image de couverture optionnelle
    bpm = models.PositiveIntegerField(default=120)  # BPM (tempo)
    key = models.CharField(max_length=10, blank=True, null=True)  # Clé musicale (ex: C#m, F#)
    genre = models.CharField(max_length=100, blank=True, null=True)  # Genre du beat (Hip-Hop, Trap, Afrobeat...)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Prix du beat (peut être gratuit)
    license_type = models.CharField(
        max_length=50,
        choices=[("free", "Free"), ("exclusive", "Exclusive"), ("lease", "Lease")],
        default="lease"
    )  # Type de licence
    likes = models.ManyToManyField(CustomUser, related_name="liked_beats", blank=True)  # Système de likes
    likes_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Dernière mise à jour

    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
@receiver(m2m_changed, sender=Beat.likes.through)
def update_likes_count(sender, instance, action, **kwargs):
    """
    Met à jour le nombre de likes chaque fois qu'un like est ajouté ou retiré.
    """
    if action in ["post_add", "post_remove"]:
        # Calculer et mettre à jour le nombre de likes
        instance.likes_count = instance.likes.count()
        instance.save()
        
    