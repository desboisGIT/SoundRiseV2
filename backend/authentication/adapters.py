from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        print("🚀 save_user() appelé")  # Vérifie que la fonction est exécutée
        """
        Sauvegarde et met à jour l'utilisateur avec les données du compte social.
        """
        user = super().save_user(request, sociallogin, form)  # Création du user

        # Récupérer les données du compte social
        extra_data = sociallogin.account.extra_data

        # Mise à jour du modèle utilisateur avec les données Google
        user.username = extra_data.get("name", user.email.split('@')[0])  # Nom propre
        user.first_name = extra_data.get("given_name", "")
        user.last_name = extra_data.get("family_name", "")
        user.email = extra_data.get("email", user.email)  # Vérifie l'email
        user.profile_picture = extra_data.get("picture", "")

        user.save()  # Sauvegarde des modifications

        return user
