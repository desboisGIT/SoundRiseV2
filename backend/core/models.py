
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator, EmailValidator
from django.utils.translation import gettext_lazy as _
import urllib.parse

class CustomUserManager(BaseUserManager):
    """Gestionnaire de création des utilisateurs et superutilisateurs"""
    
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_("L'email est obligatoire"))
        if not username:
            raise ValueError(_("Le nom d'utilisateur est obligatoire"))
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)  # Hashage du mot de passe
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Un superutilisateur doit avoir is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Un superutilisateur doit avoir is_superuser=True."))
        
        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """Modèle utilisateur personnalisé pour Soundrise"""

    email = models.EmailField(
        unique=True,
        validators=[EmailValidator(message=_("Veuillez entrer un email valide."))],
    )
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            MinLengthValidator(3, message=_("Le nom d'utilisateur doit contenir au moins 3 caractères.")),
            RegexValidator(r"^[a-zA-Z0-9_.-]+$", _("Le nom d'utilisateur ne peut contenir que des lettres, chiffres, points, tirets et underscores."))
        ]
    )
    
    password = models.CharField(
        max_length=128,  
        validators=[
            MinLengthValidator(8, message=_("Le mot de passe doit contenir au moins 8 caractères.")),
            RegexValidator(r".*[A-Z]", _("Le mot de passe doit contenir au moins une lettre majuscule.")),
            RegexValidator(r".*[a-z]", _("Le mot de passe doit contenir au moins une lettre minuscule.")),
            RegexValidator(r".*\d", _("Le mot de passe doit contenir au moins un chiffre.")),
            RegexValidator(r".*[@$!%*?&]", _("Le mot de passe doit contenir au moins un caractère spécial (@$!%*?&)."))
        ]
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_online = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)
    
    
    profile_picture = models.ImageField(upload_to="profile_pics/", null=True, blank=True, default="profile_pics/default_profile.png")

    bio = models.TextField(blank=True, null=True)
    followers = models.ManyToManyField("self", symmetrical=False, related_name="following", blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    
    def __str__(self):  
        return self.username
    
    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            path = obj.profile_picture.url.replace("/media/", "")
            return urllib.parse.unquote(path)  # Décodage ici
        return None
    
    def save(self, *args, **kwargs):
        from .tasks import convert_profile_picture_task
        is_new_upload = self.pk is None or "profile_picture" in kwargs.get("update_fields", [])

        super().save(*args, **kwargs)  # Sauvegarde l'image originale

        if is_new_upload and self.profile_picture:
            # Lancer la tâche Celery pour convertir uniquement les uploads
            convert_profile_picture_task.delay(self.id)



