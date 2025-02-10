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
        




def google_callback(request):
    # Logique pour gérer la réponse de Google
    return redirect('/')  # Redirige vers la page d'accueil de base Django

