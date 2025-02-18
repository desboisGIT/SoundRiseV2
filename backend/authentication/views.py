from django.shortcuts import render,redirect
import requests
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .serializers import RegisterSerializer,generate_verification_token 
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
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
import logging
from rest_framework.decorators import api_view
from google.auth.transport.requests import Request
from google.oauth2 import id_token
logger = logging.getLogger(__name__)
from django.http import JsonResponse
import requests
import json

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
        # Check suspicious IP
        ip, _ = get_client_ip(request)
        if is_suspicious_ip(request):
            return Response({"error": "Connexion bloquée pour cette IP."}, status=status.HTTP_403_FORBIDDEN)
        
        # Use the default logic to validate user credentials and generate tokens
        response = super().post(request, *args, **kwargs)

        # If successful, mark the user as online
        if response.status_code == 200:
            user = CustomUser.objects.get(email=request.data.get("email"))
            user.is_online = True
            user.save(update_fields=["is_online"])

            # Extract tokens from the response data
            data = response.data
            access_token = data.get("access")
            refresh_token = data.get("refresh")

            # Instead of storing the access token in a cookie, store the REFRESH token in a cookie
            # That way, the access token remains short-lived and stored in-memory on the client
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,      # Prevents JS from reading it
                secure=True,        # In dev: can be False if you're not on HTTPS
                samesite="None"     # Typically needed if you're handling cross-site flows (Google OAuth, etc.)
            )

            # (Optionally) remove the refresh token from the response body so it’s not exposed to JavaScript
            # If you don't remove it, you risk having it in plain JSON. It's up to you.
            data.pop("refresh", None)

            # The final response should still contain the access token so you can store it in your client’s memory (React state, Redux, etc.)
            response.data = data

        return response

class CustomTokenRefreshView(APIView):
    """
    Custom Refresh Token view.
    Attempts to obtain the refresh token from the request data first.
    If not provided, it falls back to reading it from the request cookies.
    """
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            refresh_token = request.COOKIES.get("refresh_token")
        
        if not refresh_token:
            return Response({"error": "No refresh token provided."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            # Optionally: If ROTATE_REFRESH_TOKENS is enabled, rotate here and set a new cookie.
            new_access = str(token.access_token)
            return Response({"access": new_access}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh", None)
            if not refresh_token:
                return Response({"error": "Le token de rafraîchissement est requis"}, status=status.HTTP_400_BAD_REQUEST)

            # Vérifier si l'utilisateur est bien authentifié
            if not request.user.is_authenticated:
                return Response({"error": "Utilisateur non authentifié"}, status=status.HTTP_401_UNAUTHORIZED)

            # Essayer d'invalider le token (nécessite la blacklisting activée)
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()  # Vérifie bien que la blacklist est activée
            except AttributeError:
                logger.error("Blacklist non activée. Assure-toi que SIMPLE_JWT['TOKEN_BLACKLIST'] = True")
                return Response({"error": "La blacklist des tokens n'est pas activée"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                logger.error(f"Erreur lors de l'invalidation du token: {str(e)}")
                return Response({"error": "Token invalide ou déjà blacklisté"}, status=status.HTTP_400_BAD_REQUEST)

            # Mettre à jour `is_online = False`
            user = request.user
            user.is_online = False
            user.save(update_fields=["is_online"])

            return Response({"message": "Déconnexion réussie"}, status=status.HTTP_204_NO_CONTENT)

        except Exception as e:
            logger.error(f"Erreur générale lors de la déconnexion: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

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

from django.views.decorators.csrf import csrf_exempt


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }

@csrf_exempt
def google_callback(request):
    """
    Google callback endpoint:
    - Verifies the Google id_token.
    - Finds or creates a user linked to the Google account.
    - Generates JWT tokens.
    - Logs in the user.
    - Returns the access token in the JSON response.
    - Stores the refresh token in a secure, HttpOnly cookie.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        # Parse the incoming JSON data to retrieve the id_token
        data = json.loads(request.body)
        token_id = data.get("token")
        if not token_id:
            return JsonResponse({"error": "No token provided"}, status=400)

        # Verify the token with Google's tokeninfo endpoint
        token_url = "https://oauth2.googleapis.com/tokeninfo"
        token_response = requests.get(f"{token_url}?id_token={token_id}")
        if token_response.status_code != 200:
            return JsonResponse({"error": "Invalid token"}, status=400)
        user_info = token_response.json()

        # Extract necessary user details from Google
        google_id = user_info.get("sub")
        google_email = user_info.get("email")
        google_name = user_info.get("name")
        if not google_id or not google_email:
            return JsonResponse({"error": "Invalid user data from Google"}, status=400)

        # Find existing SocialAccount or create a new user and SocialAccount
        try:
            social_account = SocialAccount.objects.get(uid=google_id, provider="google")
            user = social_account.user
        except SocialAccount.DoesNotExist:
            user, created = CustomUser.objects.get_or_create(
                email=google_email,
                defaults={"username": google_name}
            )
            social_account = SocialAccount.objects.create(
                user=user,
                provider="google",
                uid=google_id,
                extra_data=user_info,
            )

        # Generate JWT tokens (access and refresh) for the user
        tokens = get_tokens_for_user(user)  # returns a dict with keys "access" and "refresh"

        # Log the user in using the allauth backend
        user.backend = "allauth.account.auth_backends.AuthenticationBackend"
        login(request, user, backend=user.backend)

        # Prepare the JSON response with the access token
        response = JsonResponse({
            "message": "Login successful",
            "access": tokens["access"],
        })

        # Store the refresh token in a secure HttpOnly cookie
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh"],
            httponly=True,     # Prevents JS access to the cookie
            secure=True,       # Set to False in dev if not using HTTPS
            samesite="None"     # For cross-site usage (adjust in production as needed)
        )

        return response

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    except Exception as e:
        print("Error in google_callback:", str(e))
        return JsonResponse({"error": "Internal Server Error"}, status=500)



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

