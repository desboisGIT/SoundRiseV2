from django.db import models
from core.models import CustomUser
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.timezone import now



class Beat(models.Model):
    """
    Modèle représentant un beat musical sur Soundrise.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="beats")  # Créateur du beat
    title = models.CharField(max_length=255)  # Titre du beat
    cover_image = models.ImageField(upload_to="beats/covers/", blank=True, null=True)  # Image de couverture optionnelle
    bpm = models.PositiveIntegerField(default=120)  # BPM (tempo)
    key = models.CharField(max_length=10, blank=True, null=True)  # Clé musicale (ex: C#m, F#)
    genre = models.CharField(max_length=100, blank=True, null=True)  # Genre du beat (Hip-Hop, Trap, Afrobeat...)

    # Artistes associés
    main_artist = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="main_beats")  # Artiste principal
    co_artists = models.ManyToManyField(CustomUser, related_name="featured_beats", blank=True)  # Co-artistes

    # Système de likes
    likes = models.ManyToManyField(CustomUser, related_name="liked_beats", blank=True)
    likes_count = models.IntegerField(default=0)

    # Promotion
    promo_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Réduction en %")
    promo_end_date = models.DateTimeField(blank=True, null=True, help_text="Date de fin de la promotion")

    # Statut du beat
    is_public = models.BooleanField(default=True, help_text="Définit si le beat est public ou privé.")  # Visibilité
    is_sold = models.BooleanField(default=False, help_text="Indique si le beat a été vendu en exclusivité.")  # Statut de vente

    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Dernière mise à jour

    @property
    def price(self):
        """
        Retourne le prix du beat basé sur la licence la moins chère.
        Applique la promotion si elle est encore valide.
        """
        min_price = self.licenses.aggregate(models.Min('price')).get('price__min', 0.00)

        # Convertir None en 0.00 pour éviter toute erreur
        min_price = float(min_price) if min_price is not None else 0.00

        # Assurer que promo_discount est un float valide et appliquer la promo si elle est active
        promo = float(self.promo_discount) if self.promo_discount else 0.00
        if promo > 0 and self.promo_end_date and self.promo_end_date > now():
            return round(min_price * (1 - promo / 100), 2)

        return min_price



    def __str__(self):
        return f"{self.title} - {self.user.username}"


class BeatTrack(models.Model):
    """
    Modèle pour gérer plusieurs pistes audio associées à un Beat.
    """
    beat = models.ForeignKey(Beat, on_delete=models.CASCADE, related_name="tracks")
    title = models.CharField(max_length=255, help_text="Titre de la piste (Ex: Version MP3, WAV, Stems...)")
    audio_file = models.FileField(upload_to="beats/audio/")
    file_type = models.CharField(
        max_length=50,
        choices=[("mp3", "MP3"), ("wav", "WAV"), ("stems", "Stems"), ("other", "Autre")],
        default="mp3"
    )  # Type de fichier

    def __str__(self):
        return f"{self.title} - {self.beat.title}"


class License(models.Model):
    """
    Modèle de licence permettant aux utilisateurs de définir leurs propres licences pour un beat.
    """
    beat = models.ForeignKey(Beat, on_delete=models.CASCADE, related_name="licenses")
    title = models.CharField(max_length=255)  # Nom de la licence (Ex: Basic Lease, Premium, Exclusive...)
    description = models.TextField(blank=True, null=True)  # Description de la licence
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Prix de la licence

    # Pistes audio incluses dans cette licence
    tracks = models.ManyToManyField(BeatTrack, related_name="licenses")

    # Fichiers associés à la licence
    license_file = models.FileField(upload_to="licenses/files/", blank=True, null=True)  # Contrat PDF ou document
    terms_text = models.TextField(blank=True, null=True)  # Texte de la licence
    is_exclusive = models.BooleanField(default=False, help_text="Indique si cette licence est exclusive.")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.beat.title} ({'Exclusive' if self.is_exclusive else 'Non-Exclusive'})"
    


@receiver(m2m_changed, sender=Beat.likes.through)
def update_likes_count(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove"]:
        instance.likes_count = instance.likes.count()
        instance.save()

    