from celery import shared_task
from PIL import Image
import os
from io import BytesIO
from django.core.files.base import ContentFile
from .models import CustomUser

def convert_to_webp(image_field):
    """Convertit une image en WebP sauf si elle est déjà en WebP ou une URL externe"""
    img = Image.open(image_field)

    # Vérifier si l'image est déjà WebP
    if img.format == "WEBP":
        return image_field

    # Convertir en mode RGB pour éviter les problèmes avec PNG
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Créer un buffer mémoire pour stocker l'image WebP
    output = BytesIO()
    img.save(output, format="WEBP", quality=85)
    output.seek(0)

    # Retourner le fichier Django avec extension WebP
    return ContentFile(output.read(), name=f"{os.path.splitext(image_field.name)[0]}.webp")

@shared_task
def convert_profile_picture_task(user_id):
    """Tâche Celery pour convertir la photo de profil en WebP"""
    user = CustomUser.objects.get(id=user_id)

    

    # Vérifier si c'est un upload local
    if "profile_pics" in user.profile_picture.url:
        user.profile_picture = convert_to_webp(user.profile_picture)
        user.save()
    
    # Vérifier si l'image vient de Google (URL externe)
    else :
        return  # Ne pas convertir
