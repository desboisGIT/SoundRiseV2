from django.shortcuts import render,redirect

# Create your views here.
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import RegisterSerializer,generate_verification_token 
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.conf import settings
from core.models import CustomUser
from ipware import get_client_ip
from .security import is_suspicious_ip 
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.authtoken.models import Token
import os
from django.contrib.auth import login

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_verified = False  # On bloque le compte tant qu'il n'est pas validé
            user.save()

            # Générer le token de vérification
            token = generate_verification_token(user)
            verification_link = f"http://127.0.0.1:8000/api/auth/verify/{token}/"

            # Envoyer l'email
            self.send_verification_email(user.email, verification_link)

            return Response(
                {"message": "Inscription réussie. Vérifiez votre email pour activer votre compte."},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_verification_email(self, email, verification_link):
        """ Envoie un email avec le lien de vérification """
        send_mail(
            'Vérifiez votre compte SoundRise',
            f'Cliquez sur le lien suivant pour activer votre compte : {verification_link}',
            settings.DEFAULT_FROM_EMAIL,  # Doit être configuré dans settings.py
            [email],
            fail_silently=False,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # Vérifie si l'IP est suspecte
        ip, _ = get_client_ip(request)
        if is_suspicious_ip(request):
            return Response({"error": "Connexion bloquée pour cette IP."}, status=status.HTTP_403_FORBIDDEN)
        
        # Continue le processus d'authentification
        return super().post(request, *args, **kwargs)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=204)
        except Exception as e:
            return Response(status=400)
        
class VerifyEmailView(APIView):
    def get(self, request, token, *args, **kwargs):
        """ Vérifie le token et active le compte """
        try:
            access_token = AccessToken(token)
            user = CustomUser.objects.get(id=access_token['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response({"message": "Email vérifié avec succès. Vous pouvez maintenant vous connecter."}, status=status.HTTP_200_OK)
            return Response({"message": "Votre email est déjà vérifié."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "Token invalide ou expiré."}, status=status.HTTP_400_BAD_REQUEST)



from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from allauth.socialaccount.models import SocialAccount

import os
import requests
from django.contrib.auth import login
from django.shortcuts import redirect
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from django.contrib.auth import get_user_model

User = get_user_model()

def google_callback(request):
    """
    Vérifie si un utilisateur a un compte Google. Si oui, connecte-le, sinon crée un compte.
    """
    print("🚀 google_callback() appelée")

    # Redirection si on est en GET sans code
    if request.method == "GET" and "code" not in request.GET:
        print("🔄 Requête GET sans code, redirection vers Google login...")
        return redirect("/api/auth/google/login/")

    # Récupérer le code envoyé par Google
    code = request.GET.get("code")

    # Échanger le code contre un token d'accès Google
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY"),
        "client_secret": os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET"),
        "redirect_uri": "http://127.0.0.1:8000/api/auth/google/callback/",
        "grant_type": "authorization_code",
    }

    token_response = requests.post(token_url, data=data)
    token_json = token_response.json()

    if "access_token" not in token_json:
        print("❌ Échec de l'obtention du token Google :", token_json)
        return redirect("/api/auth/google/login/")

    access_token = token_json["access_token"]

    # Obtenir les informations utilisateur de Google
    user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_data = user_info_response.json()

    google_id = user_data.get("sub")
    google_email = user_data.get("email")
    google_name = user_data.get("name", google_email.split("@")[0])
    first_name = user_data.get("given_name", "")
    last_name = user_data.get("family_name", "")
    profile_picture = user_data.get("picture", "")

    if not google_id or not google_email:
        print("❌ Données utilisateur Google incomplètes :", user_data)
        return redirect("/api/auth/google/login/")

    # Vérifier si un SocialAccount existe déjà
    try:
        social_account = SocialAccount.objects.get(uid=google_id, provider="google")
        user = social_account.user
        print("✅ Compte Google trouvé :", user)

    except SocialAccount.DoesNotExist:
        print("❌ Aucun compte Google trouvé, création d'un utilisateur...")

        # Vérifier si un utilisateur avec cet email existe déjà
        user, created = User.objects.get_or_create(email=google_email, defaults={
            "username": google_name,
            "email": google_email,
            "profile_picture": profile_picture,
        
        })

        if created:
            print("✅ Nouvel utilisateur créé :", user)
        else:
            print("⚠️ Un utilisateur avec cet email existe déjà mais sans compte Google.")


        extra_data = {
            "google_id": google_id,
            "email": google_email,
            "name": google_name,
            "first_name": first_name,
            "last_name": last_name,
            "picture": profile_picture,
        }

        # Associer un SocialAccount au nouvel utilisateur
        social_account = SocialAccount.objects.create(
            user=user,
            provider="google",
            uid=google_id,
            extra_data=extra_data,
        )
        print("✅ SocialAccount créé :", social_account)

    # Connexion automatique
    user.backend = "allauth.account.auth_backends.AuthenticationBackend"
    login(request, user, backend=user.backend)
    return redirect("/")


class GoogleLoginView(SocialLoginView):
    def get(self, request, *args, **kwargs):
        client_id = os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY')
        redirect_url = f"https://accounts.google.com/o/oauth2/auth?client_id={client_id}&redirect_uri=http://127.0.0.1:8000/api/auth/google/callback/&response_type=code&scope=openid email profile"
        print("URL OAuth :", redirect_url)
        return redirect(redirect_url)
    """
    Vue qui gère l'authentification avec Google OAuth2.
    Si l'utilisateur n'a pas de compte, il en crée un.
    """
    adapter_class = GoogleOAuth2Adapter