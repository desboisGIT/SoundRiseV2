from django.db import models
from core.models import CustomUser
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.timezone import now
from mutagen import File
from multiselectfield.db.fields import MultiSelectField
from django.db.models.signals import pre_delete,post_save
from django.core.exceptions import ValidationError







class Beat(models.Model):
    """
    Modèle représentant un beat musical sur Soundrise.
    """
    
    title = models.CharField(max_length=255)  # Titre du beat
    cover_image = models.ImageField(upload_to="beats/covers/", blank=True, null=True)  # Image de couverture optionnelle
    bpm = models.PositiveIntegerField(default=120)  # BPM (tempo)
    key = models.CharField(max_length=10, blank=True, null=True)  # Clé musicale (ex: C#m, F#)
    genre = models.CharField(max_length=100, blank=True, null=True)  # Genre du beat (Hip-Hop, Trap, Afrobeat...)
    hashtags = models.ManyToManyField("Hashtag", related_name="beats", blank=True)
    is_free =models.BooleanField(default=True, help_text="Définit si le beat est gratuiit ou payant.")  # Visibilité
    duration = models.FloatField(blank=True, null=True, help_text="Durée de la piste sélectionnée en secondes")  # Durée de la piste sélectionnée
    # Artistes associés
    main_artist = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="beats")
    co_artists = models.ManyToManyField(CustomUser, related_name="featured_beats", blank=True)  # Co-artistes

    # models liés
    licenses = models.ManyToManyField('License', related_name="beat")


    # Système de likes
    likes = models.ManyToManyField(CustomUser, related_name="liked_beats", blank=True)
    likes_count = models.IntegerField(default=0)

    #favorites
    favorites = models.ManyToManyField(CustomUser, related_name="favorited_beats", blank=True)
    favorites_count = models.IntegerField(default=0)


    #vues 
    views = models.ManyToManyField("BeatView", related_name="view_beat", blank=True)

    # Promotion
    promo_discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text="Réduction en %")
    promo_end_date = models.DateTimeField(blank=True, null=True, help_text="Date de fin de la promotion")

    # Statut du beat
    is_sold = models.BooleanField(default=False, help_text="Indique si le beat a été vendu en exclusivité.")  # Statut de vente

    created_at = models.DateTimeField(auto_now_add=True)  # Date de création
    updated_at = models.DateTimeField(auto_now=True)  # Dernière mise à jour

    
    audio_file=models.FileField(upload_to='beats/audio_file', null=True, blank=True)

    #files
    mp3 = models.FileField(upload_to='beats/%Y/%m/%d/', null=True, blank=True)
    wav = models.FileField(upload_to='beats/%Y/%m/%d/', null=True, blank=True)
    flac = models.FileField(upload_to='beats/%Y/%m/%d/', null=True, blank=True)
    ogg = models.FileField(upload_to='beats/%Y/%m/%d/', null=True, blank=True)
    aac = models.FileField(upload_to='beats/%Y/%m/%d/', null=True, blank=True)
    alac = models.FileField(upload_to='beats/%Y/%m/%d/', null=True, blank=True)
    zip = models.FileField(upload_to='beats/%Y/%m/%d/', null=True, blank=True)

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
        Sélectionne le fichier audio optimal parmi les formats disponibles.
        Gère aussi les formats inconnus.
        """
        # Tous les formats audio disponibles dans le modèle Beat
        available_formats = {
            '.mp3': self.mp3,
            '.wav': self.wav,
            '.flac': self.flac,
            '.ogg': self.ogg,
            '.aac': self.aac,
            '.alac': self.alac
        }

        # Formats préférés, avec les formats inconnus à la fin
        preferred_formats = ['.m4a', '.opus', '.mp3', '.ogg', '.wav', '.flac', '.aac', '.alac']

        # Filtrer les fichiers audio non présents
        available_files = [
            {'file': file, 'file_type': ext}
            for ext, file in available_formats.items() if file
        ]

        # Trier les fichiers par priorité de format, les formats inconnus étant mis à la fin
        sorted_files = sorted(
            available_files,
            key=lambda af: preferred_formats.index(af['file_type']) if af['file_type'] in preferred_formats else len(preferred_formats)
        )

        # Gérer les formats inconnus
        for af in available_files:
            if af['file_type'] not in preferred_formats:
                print(f"⚠️ Format inconnu détecté: {af['file_type']} pour {af['file']}")

        # Sélectionner le meilleur fichier audio disponible
        if sorted_files:
            best_file = sorted_files[0]  # Prend le premier fichier après tri
            self.audio_file = best_file['file']
            self.file_type = best_file['file_type']  # Mettre à jour le type de fichier

            # Mettre à jour la durée en fonction du fichier audio
            audio = File(self.audio_file)
            self.duration = audio.info.length if audio else 0

    def save(self, *args, **kwargs):
        """
        Méthode personnalisée save pour éviter la boucle infinie et appeler select_best_audio().
        """
        # Appeler select_best_audio pour sélectionner le meilleur fichier audio et mettre à jour la durée
        self.select_best_audio()

        # Appeler la méthode save d'origine pour sauvegarder l'objet sans recréer une boucle infinie
        super(Beat, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Beat"
        verbose_name_plural = "Beats"
            
    @property
    def total_views(self):
        return self.views.count()  # Compte toutes les vues enregistrées
    


    


    def __str__(self):
        return f"{self.title} - {self.main_artist.username}"


@receiver(m2m_changed, sender=Beat.likes.through)
def update_likes_count(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove"]:
        instance.likes_count = instance.likes.count()
        instance.save()

@receiver(m2m_changed, sender=Beat.favorites.through)
def update_likes_count(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove"]:
        instance.favorites_count = instance.favorites.count()
        instance.save()



class BeatView(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)  
    beat = models.ForeignKey("Beat", on_delete=models.CASCADE, related_name="beat_views")  # Changer le related_name    
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Vue par IP
    viewed_at = models.DateTimeField(auto_now_add=True)  # Date de la vue

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["beat", "user"], name="unique_user_beat_view"),
            models.UniqueConstraint(fields=["beat", "ip_address"], name="unique_ip_beat_view")
        ]


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
    conditions = models.JSONField(default=list, blank=True)  # Liste 2D sous forme JSON

    is_exclusive = models.BooleanField(default=False, help_text="Indique si cette licence est exclusive.")
    
    created_at = models.DateTimeField(auto_now_add=True)



    def clean(self):
        # Si la licence est associée à un beat et que le template n'est pas 'custom'
        if hasattr(self, 'beats') and self.beats.exists() and self.license_template != 'CUSTOM':
            raise ValidationError(_("Impossible de modifier ou de supprimer une licence associée à un beat, sauf si elle utilise le modèle 'custom'."))
        
        # Si la licence est 'custom', vérifier les modifications permises
        if self.license_template == 'CUSTOM':
            allowed_fields = ['title', 'description', 'price']
            changed_fields = self.get_dirty_fields()

            for field in changed_fields:
                if field not in allowed_fields:
                    raise ValidationError(f"Le champ '{field}' ne peut être modifié que si le modèle de licence est 'CUSTOM'.")


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_values = self._get_current_values()

    def _get_current_values(self):
        """Récupère les valeurs actuelles de tous les champs"""
        return {
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'license_template': self.license_template,
            'license_file_types': self.license_file_types,
            'terms_text': self.terms_text,
            'is_exclusive': self.is_exclusive,
            'conditions': self.conditions,
        }

    def get_dirty_fields(self):
        """Retourne les champs qui ont changé"""
        dirty_fields = {}
        for field, original_value in self._original_values.items():
            current_value = getattr(self, field)
            if current_value != original_value:
                dirty_fields[field] = current_value
        return dirty_fields

    def delete(self, *args, **kwargs):
        # Vérifiez si cette licence est la seule associée à un beat
        if self.license_template != 'custom':
            raise ValidationError(f"Vous ne pouvez pas supprimer cette license car c'est une templates.")
        for beat in self.beats.all():
            # Si le beat a exactement une seule licence (celle-ci), on lève une erreur
            if beat.licenses.count() == 1:
                raise ValidationError(f"Le beat '{beat.title}' n'a plus d'autres licences. Impossible de supprimer cette licence.")
            
            # Si le beat a d'autres licences associées, on met simplement la licence en is_active=False
            if beat.licenses.count() > 1:
                self.is_active = False
                self.save()  # Sauvegarder la modification du statut de la licence
                return  # Ne pas continuer à supprimer, on désactive juste la licence

        # Si aucun beat n'a d'autre licence, on supprime la licence
        super().delete(*args, **kwargs)

            
    def save(self, *args, **kwargs):
        """Remplit automatiquement les informations si un template est sélectionné."""
        

        if self.license_template != "CUSTOM":
            templates_data = {
    "BASIC": {
        "title": "Basic License",
        "description": "License basique avec utilisation commerciale limitée.",
        "terms_text": "Non-exclusive, max 100k streams.",
        "license_file_types": ["mp3"],  # Seulement MP3 pour une licence basique
        "is_exclusive": False,
    },
    "PREMIUM": {
        "title": "Premium License",
        "price": 99.99,
        "description": "License premium avec droits commerciaux étendus.",
        "terms_text": "Non-exclusive, streams illimités, monétisation autorisée.",
        "license_file_types": ["mp3", "wav"],  # Formats de meilleure qualité inclus
        "is_exclusive": False,
    },
    "UNLIMITED": {
        "title": "Unlimited License",
        "price": 199.99,
        "description": "Streams, ventes et monétisation illimités.",
        "terms_text": "Non-exclusive, pas de limite d’utilisation.",
        "license_file_types": ["mp3", "wav", "flac"],  # Qualité maximale pour une licence illimitée
        "is_exclusive": False,
    },
    "EXCLUSIVE": {
        "title": "Exclusive License",
        "price": 499.99,
        "description": "Vous obtenez tous les droits sur le beat.",
        "terms_text": "Exclusive, pas de limite d’utilisation.",
        "license_file_types": ["mp3", "wav", "flac", "stems"],  # Inclut les stems pour modification complète
        "is_exclusive": True,
    },
    "RADIO": {
        "title": "Radio License",
        "price": 149.99,
        "description": "Licence pour diffusion radio avec redevance SACEM.",
        "terms_text": "Utilisation radio autorisée, pas de vente directe.",
        "license_file_types": ["mp3", "wav"],  # Radio nécessite du WAV pour qualité broadcast
        "is_exclusive": False,
    },
    "TV": {
        "title": "TV License",
        "price": 299.99,
        "description": "Licence autorisant l’utilisation pour la télévision et les films.",
        "terms_text": "Droits TV et cinéma accordés.",
        "license_file_types": ["wav", "flac", "stems"],  # Qualité maximale et possibilité de mixage
        "is_exclusive": False,
    },
    "SYNC": {
        "title": "Sync License",
        "price": 399.99,
        "description": "Utilisation du beat pour des publicités, films et jeux vidéo.",
        "terms_text": "Droits de synchronisation pour médias accordés.",
        "license_file_types": ["wav", "flac", "stems", "zip"],  # Inclut stems et pack complet pour synchronisation
        "is_exclusive": False,
    }
}
            # Appliquer les valeurs du template
            template_values = templates_data.get(self.license_template, {})
            for field, value in template_values.items():
                setattr(self, field, value)

        self.clean() 
        super(License, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {('Exclusive' if self.is_exclusive else 'Non-Exclusive')}"

@receiver(post_save, sender=CustomUser)
def create_default_licenses(sender, instance, created, **kwargs):
    if created:
        # Créer une licence pour chaque template à la création de l'utilisateur
        templates = ["BASIC", "PREMIUM", "UNLIMITED", "EXCLUSIVE", "RADIO", "TV", "SYNC"]
        for template in templates:
            License.objects.create(
                user=instance,
                license_template=template
            )





class DraftBeat(models.Model):
    """Modèle pour stocker un Beat en brouillon avec plusieurs Licenses ."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  
    title = models.CharField(max_length=255, blank=True, null=True)
    bpm = models.IntegerField(blank=True, null=True)
    key = models.CharField(max_length=10, blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    hashtags = models.ManyToManyField("Hashtag", related_name="draftbeats", blank=True)
    cover_image = models.ImageField(upload_to="draft/covers/", blank=True, null=True)  # Image de couverture optionnelle
    
    co_artists =models.ManyToManyField(CustomUser, related_name="featured_draft_beats", blank=True)  # Co-artistes

    # ✅ Stockage des Licenses et Tracks sous forme de liste JSON 
    licenses = models.ManyToManyField(License, blank=True)

    #files
    mp3 = models.FileField(upload_to='beats/%Y/%m/%d/', null=True, blank=True)
    wav = models.FileField(upload_to='beats/%Y/%m/%d/', null=True, blank=True)
    flac = models.FileField(upload_to='beats/%Y/%m/%d/', null=True, blank=True)
    ogg = models.FileField(upload_to='beats/%Y/%m/%d/', null=True, blank=True)
    aac = models.FileField(upload_to='beats/%Y/%m/%d/', null=True, blank=True)
    alac = models.FileField(upload_to='beats/%Y/%m/%d/', null=True, blank=True)
    zip = models.FileField(upload_to='beats/%Y/%m/%d/', null=True, blank=True)

    

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
        






class Hashtag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class CollaborationInvite(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_invites")
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_invites")
    draftbeat = models.ForeignKey(DraftBeat, on_delete=models.CASCADE)
    status = models.CharField(
        choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('refused', 'Refused'), ('expired', 'Expired')],
        default='pending',
        max_length=20
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def accept(self):
        self.status = 'accepted'
        self.save()
        self.beat.collaborators.add(self.recipient)

    def refuse(self):
        self.status = 'refused'
        self.save()