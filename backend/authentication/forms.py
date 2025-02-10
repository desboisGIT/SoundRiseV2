# authentication/forms.py
from allauth.socialaccount.forms import SignupForm
from django.utils.text import slugify

class SocialSignupForm(SignupForm):
    def save(self, request):
        # Récupère l'utilisateur de manière automatique
        user = super(SocialSignupForm, self).save(request)
        
        # Créer un username unique à partir de l'email de l'utilisateur
        username = slugify(user.email.split('@')[0])  # Prend la première partie de l'email comme base
        
        # Assigner le username
        user.username = username
        
        # Sauvegarder l'utilisateur avec le nouveau username
        user.save()
        
        return user
