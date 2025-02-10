from django.contrib.auth import get_user_model
from allauth.socialaccount.signals import social_account_added, social_account_updated
from django.dispatch import receiver
from django.utils.text import slugify

User = get_user_model()  # Récupère ton modèle CustomUser

@receiver(social_account_added)
@receiver(social_account_updated)
def update_user_profile(sender, request, sociallogin, **kwargs):
    """
    Met à jour les informations de l'utilisateur à partir des données Google.
    """
    print("🔥 Signal `social_account_added/social_account_updated` reçu !")  # Debug

    user = sociallogin.user  # Récupération de l'utilisateur
    google_data = sociallogin.account.extra_data  # Données Google

    print("📢 Google Data :", google_data)  # Vérification des données récupérées

    # Mettre à jour l'utilisateur avec les données de Google
    if not user.username or user.username.startswith("user_"):
        user.username = slugify(google_data.get("name", user.email.split('@')[0]))  # Nom propre
    if "email" in google_data:
        user.email = google_data["email"]
    if "given_name" in google_data:
        user.first_name = google_data["given_name"]
    if "family_name" in google_data:
        user.last_name = google_data["family_name"]
    if "picture" in google_data:
        user.profile_picture = google_data["picture"]  # Assure-toi que ce champ existe dans ton `CustomUser`

    user.save()  # Sauvegarde des modifications

    print(f"✅ Utilisateur mis à jour : {user.username} ({user.first_name} {user.last_name})")
