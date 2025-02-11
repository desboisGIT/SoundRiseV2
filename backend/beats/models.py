from django.db import models
from core.models import CustomUser


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
    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Dernière mise à jour

    def __str__(self):
        return f"{self.title} - {self.user.username}"
