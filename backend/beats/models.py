from django.db import models
from core.models import CustomUser
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.timezone import now
from mutagen import File
from multiselectfield.db.fields import MultiSelectField



class Beat(models.Model):
    """
    Modèle représentant un beat musical sur Soundrise.
    """
    
    title = models.CharField(max_length=255)  # Titre du beat
    cover_image = models.ImageField(upload_to="beats/covers/", blank=True, null=True)  # Image de couverture optionnelle
    bpm = models.PositiveIntegerField(default=120)  # BPM (tempo)
    key = models.CharField(max_length=10, blank=True, null=True)  # Clé musicale (ex: C#m, F#)
    genre = models.CharField(max_length=100, blank=True, null=True)  # Genre du beat (Hip-Hop, Trap, Afrobeat...)

    main_track = models.ForeignKey('BeatTrack', on_delete=models.SET_NULL, null=True, blank=True, related_name='main_beats')  # Piste principale sélectionnée
    duration = models.FloatField(blank=True, null=True, help_text="Durée de la piste sélectionnée en secondes")  # Durée de la piste sélectionnée
    audio_file = models.FileField(upload_to="beats/audio_files/", blank=True, null=True)  # Fichier sélectionné automatiquement
    # Artistes associés
    main_artist = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="beats")  # Artiste principal
    co_artists = models.ManyToManyField(CustomUser, related_name="featured_beats", blank=True)  # Co-artistes

    # models liés
    tracks = models.ManyToManyField('BeatTrack', related_name="beat")
    licenses = models.ManyToManyField('License', related_name="beat")


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

    likes = models.ManyToManyField(CustomUser, related_name="liked_beats", blank=True)
    favorites = models.ManyToManyField(CustomUser, related_name="favorited_beats", blank=True)

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

    def select_best_audio(self):
        """
        Sélectionne le fichier audio optimal parmi les tracks disponibles.
        Gère aussi les formats inconnus.
        """
        preferred_formats = ['.m4a', '.opus', '.mp3', '.ogg', '.wav', '.flac']
        
        # Récupérer toutes les pistes associées au Beat
        tracks = self.tracks.all()

        # Trier les tracks par priorité de format, en mettant les formats inconnus à la fin
        sorted_tracks = sorted(
            tracks,
            key=lambda track: preferred_formats.index(track.file_type) if track.file_type in preferred_formats else len(preferred_formats)
        )

        # Gérer les formats inconnus
        for track in tracks:
            if track.file_type not in preferred_formats:
                print(f"⚠️ Format inconnu détecté: {track.file_type} pour {track.audio_file}")

        # Sélectionner la meilleure piste disponible
        if sorted_tracks:
            best_track = sorted_tracks[0]  # Prend le premier fichier après tri
            self.audio_file = best_track.audio_file
            self.duration = best_track.duration  # Mettre à jour la durée du beat
            self.file_type = best_track.file_type  # Mettre à jour le type de fichier
            self.main_track = best_track  # Mettre à jour la piste principale
            


    def save(self, *args, **kwargs):
        """
        Surcharge du save pour sélectionner automatiquement l'audio_file avant sauvegarde.
        Appel de select_best_audio si tracks a été modifié.
        """
        # Éviter l'appel en boucle en vérifiant que select_best_audio() n'est pas déjà appelé
        if not hasattr(self, '_selecting_best_audio'):
            self._selecting_best_audio = True
            # Vérifier si les tracks ont été modifiés
            if self.tracks.count() > 0:
                self.select_best_audio()
        if self.duration : 
            self.duration = round(self.duration, 2)

        super().save(*args, **kwargs)  # Sauvegarde initiale
        delattr(self, '_selecting_best_audio')  # Supprimer l'indicateur après sauvegarde


    def __str__(self):
        return f"{self.title} - {self.main_artist.username}"




class BeatComment(models.Model):
    beat = models.ForeignKey("Beat", on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]  # Les commentaires les plus récents en premier

    def __str__(self):
        return f"{self.user.username} - {self.beat.title}"





class BeatTrack(models.Model):
    """
    Modèle pour gérer plusieurs pistes audio associées à un Beat.
    """
    
    title = models.CharField(max_length=255, help_text="Titre de la piste (Ex: Version MP3, WAV, Stems...)")
    audio_file = models.FileField(upload_to="beats/audio-track/")
    file_type = models.CharField(max_length=10, blank=True, null=True)  # Type de fichier
    duration = models.FloatField(blank=True, null=True, help_text="Durée de la piste en secondes")

    def save(self, *args, **kwargs):
        # Remplir automatiquement le type de fichier
        if self.audio_file:
            self.file_type = f".{self.audio_file.name.split('.')[-1]}"
            
        
        # Remplir automatiquement la durée de la piste
        if self.audio_file:
            # Utilisation de pydub pour obtenir la durée de la piste
            audio = File(self.audio_file)
            duration = audio.info.length if audio else 0
            
            # Arrondir la durée à deux décimales
            self.duration = round(duration, 2)
            

        super().save(*args, **kwargs)
    
    @staticmethod
    def get_file_by_type(beat, file_type):
        """
        Retourne le fichier d'un Beat selon le type demandé (.mp3, .wav, .zip, etc.).
        """
        return BeatTrack.objects.filter(beat=beat, file_type=file_type).first()

    def __str__(self):
        return f"{self.title} "


class License(models.Model):
    """
    Modèle de licence permettant aux utilisateurs de définir leurs propres licences pour un beat.
    """
    FILE_CHOICES = [
        ("mp3", "MP3"),
        ("wav", "WAV"),
        ("flac", "FLAC"),
        ("stems", "STEMS"),
        ("zip", "ZIP"),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  # Créateur de la licence
    title = models.CharField(max_length=255)  # Nom de la licence (Ex: Basic Lease, Premium, Exclusive...)
    description = models.TextField(blank=True, null=True)  # Description de la licence
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Prix de la licence

    # Pistes audio incluses dans cette licence
    tracks = models.ManyToManyField(BeatTrack, related_name="licenses",null=True, blank=True)

    TEMPLATE_CHOICES = [
        ("CUSTOM", "Custom"),       # Créée à partir du brouillon
        ("BASIC", "Basic"),         # License basique avec peu de droits
        ("PREMIUM", "Premium"),     # Version plus chère avec plus de droits
        ("UNLIMITED", "Unlimited"), # Licence sans restriction de streams
        ("EXCLUSIVE", "Exclusive"), # License où l'acheteur obtient tous les droits
        ("RADIO", "Radio"),         # Licence spécialement conçue pour la radio
        ("TV", "TV"),               # Licence avec autorisation TV et film
        ("SYNC", "Sync"),           # Licence pour les synchronisations (pub, film)
    ]

    license_template = models.CharField(
        max_length=10, choices=TEMPLATE_CHOICES, default="CUSTOM"
    )

    # Fichiers associés à la licence
    license_file_types = MultiSelectField(choices=FILE_CHOICES, blank=True, null=True)
    terms_text = models.TextField(blank=True, null=True)  # Texte de la licence
    condition = models.ManyToManyField("Conditions", related_name="licenses", blank=True)
    is_exclusive = models.BooleanField(default=False, help_text="Indique si cette licence est exclusive.")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Remplit automatiquement les informations si un template est sélectionné."""
        if self.license_template != "CUSTOM":
            templates_data = {
                "BASIC": {
                    "title": "Basic License",
                    "description": "License basique avec utilisation commerciale limitée.",
                    "terms_text": "Non-exclusive, max 100k streams.",
                    "license_file_type": "mp3",
                    "is_exclusive": False,
                },
                "PREMIUM": {
                    "title": "Premium License",
                    "price": 99.99,
                    "description": "License premium avec droits commerciaux étendus.",
                    "terms_text": "Non-exclusive, streams illimités, monétisation autorisée.",
                    "is_exclusive": False,
                },
                "UNLIMITED": {
                    "title": "Unlimited License",
                    "price": 199.99,
                    "description": "Streams, ventes et monétisation illimités.",
                    "terms_text": "Non-exclusive, pas de limite d’utilisation.",
                    "is_exclusive": False,
                },
                "EXCLUSIVE": {
                    "title": "Exclusive License",
                    "price": 499.99,
                    "description": "Vous obtenez tous les droits sur le beat.",
                    "terms_text": "Exclusive, pas de limite d’utilisation.",
                    "is_exclusive": True,
                },
                "RADIO": {
                    "title": "Radio License",
                    "price": 149.99,
                    "description": "Licence pour diffusion radio avec redevance SACEM.",
                    "terms_text": "Utilisation radio autorisée, pas de vente directe.",
                    "is_exclusive": False,
                },
                "TV": {
                    "title": "TV License",
                    "price": 299.99,
                    "description": "Licence autorisant l’utilisation pour la télévision et les films.",
                    "terms_text": "Droits TV et cinéma accordés.",
                    "is_exclusive": False,
                },
                "SYNC": {
                    "title": "Sync License",
                    "price": 399.99,
                    "description": "Utilisation du beat pour des publicités, films et jeux vidéo.",
                    "terms_text": "Droits de synchronisation pour médias accordés.",
                    "is_exclusive": False,
                }
            }
            # Appliquer les valeurs du template
            template_values = templates_data.get(self.license_template, {})
            for field, value in template_values.items():
                setattr(self, field, value)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {('Exclusive' if self.is_exclusive else 'Non-Exclusive')}"



@receiver(m2m_changed, sender=Beat.likes.through)
def update_likes_count(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove"]:
        instance.likes_count = instance.likes.count()
        instance.save()




class DraftBeat(models.Model):
    """Modèle pour stocker un Beat en brouillon avec plusieurs Licenses et Tracks."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  
    title = models.CharField(max_length=255, blank=True, null=True)
    bpm = models.IntegerField(blank=True, null=True)
    key = models.CharField(max_length=10, blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    cover_image = models.ImageField(upload_to="draft/covers/", blank=True, null=True)  # Image de couverture optionnelle
    audio_file = models.FileField(upload_to="draft/audio_files/", blank=True, null=True)  # Fichier sélectionné automatiquement
    is_public = models.BooleanField(default=True, help_text="Définit si le beat est public ou privé.")  # Visibilité

    co_artists =models.ManyToManyField(CustomUser, related_name="featured_draft_beats", blank=True)  # Co-artistes

    # ✅ Stockage des Licenses et Tracks sous forme de liste JSON 
    licenses = models.ManyToManyField(License, blank=True)
    tracks = models.ManyToManyField(BeatTrack)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Conditions(models.Model):
    """Modèle pour stocker les conditions associéés aux licences."""
    
    title = models.CharField(max_length=255)
    value = models.IntegerField(default=0, null=True, blank=True)
    is_unlimited = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Surcharge de la méthode save pour gérer la valeur illimitée."""
        if self.is_unlimited:
            self.value = None  # Remplacer la valeur par None si illimité
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title