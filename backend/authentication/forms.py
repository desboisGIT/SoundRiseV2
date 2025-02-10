from allauth.account.forms import SignupForm
from django.utils.text import slugify


class SocialSignupForm(SignupForm):
    def save(self, request):
        print("🔥 SocialSignupForm utilisé !")  # Debug

        user = super().save(request)  # Crée l'utilisateur normalement

        social_account = user.socialaccount_set.first()
        if social_account:
            google_data = social_account.extra_data  # Récupère les données de Google
            print("Google Data:", google_data)  # Vérification

            # Remplir les champs du modèle CustomUser
            if "name" in google_data:
                user.username = slugify(google_data["name"])  # Nom propre
            if "email" in google_data:
                user.email = google_data["email"]  # Assurer que l'email est bien défini
            if "picture" in google_data:  
                user.profile_picture = google_data["picture"]  # Si tu as un champ image
            if "given_name" in google_data:  
                user.first_name = google_data["given_name"]
            if "family_name" in google_data:  
                user.last_name = google_data["family_name"]

            user.save()  # Sauvegarde les modifications

        return user
