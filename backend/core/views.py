from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .serializers import CustomUserSerializer,ProfilePictureSerializer,ReportSerializer,NotificationSerializer
from .models import CustomUser,Report,Notifications
from beats.models import Beat
from .forms import ProfilePictureForm
from django.db.models import Q
from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, FormParser
from urllib.parse import urlparse, unquote
from django.shortcuts import get_object_or_404
import urllib.parse







@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Retourne les infos de l'utilisateur connecté avec `fields=` pour sélectionner les données."""
    user = request.user
    serializer = CustomUserSerializer(user, context={"request": request})

    # ✅ Gestion des champs spécifiques à retourner
    fields = request.GET.get("fields", "").split(",") if "fields" in request.GET else None

    if fields:
        valid_fields = [field.name for field in CustomUser._meta.fields]
        data = {field: serializer.data[field] for field in fields if field in serializer.data and field in valid_fields}
    else:
        data = serializer.data  # Si aucun champ n'est spécifié, retourne tout

    return Response(data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])  # L'utilisateur doit être connecté
def get_profile_picture(request):
    user = request.user

    if user.profile_picture:
        profile_picture_url = user.profile_picture.url

        if "profile_pics" in profile_picture_url:
            # Convertir en URL absolue si nécessaire
            profile_picture_url = request.build_absolute_uri(profile_picture_url)
        else:
            # Supprimer "/media/" de l'URL
            profile_picture_url = profile_picture_url.replace("/media/", "")
            # Décoder l'URL si elle contient des caractères encodés
            profile_picture_url = urllib.parse.unquote(profile_picture_url)

        return Response({"profile_picture": profile_picture_url})

    return Response({"profile_picture": None})



@api_view(["GET"])
def filter_users(request):
    """
    Filtre et affiche les utilisateurs en fonction des champs et critères choisis.
    Exemple : 
        - /api/users/filter/?id=2
        - /api/users/filter/?username=John
        - /api/users/filter/?email=...,username=...
        - /api/users/filter/?bio__isnull=false&fields=username,email
    """

    # ✅ Appliquer les filtres dynamiques sur les champs valides
    valid_fields = [field.name for field in CustomUser._meta.fields]  # Liste des champs du modèle
    filter_params = {}

    # Appliquer les filtres de recherche
    for key, value in request.GET.items():
        if key.startswith(("limit", "offset", "fields")):
            continue  # Ne pas inclure ces champs dans les filtres

        # Gestion des booléens pour isnull
        if value.lower() == "false":
            value = False
        elif value.lower() == "true":
            value = True

        # Appliquer un icontains pour `username`
        if key == "username":
            filter_params["username__icontains"] = value  # Utilisation de icontains pour la recherche insensible à la casse
        elif "__" in key:  # Gestion des filtres avancés (ex: bio__isnull=false)
            base_field = key.split("__")[0]
            if base_field in valid_fields:
                filter_params[key] = value
        else:
            base_field = key
            if base_field in valid_fields:
                filter_params[key] = value
        
    # ✅ Appliquer les filtres à la requête directement sur la base de données
    queryset = CustomUser.objects.filter(**filter_params)

    # ✅ Pagination sécurisée
    try:
        limit = max(1, int(request.GET.get("limit", 10)))  # Min = 1
    except (ValueError, TypeError):
        limit = 10  # Par défaut

    try:
        offset = max(0, int(request.GET.get("offset", 0)))  # Min = 0
    except (ValueError, TypeError):
        offset = 0  # Par défaut

    # Appliquer la pagination sur le queryset
    total_users = queryset.count()
    users = queryset[offset : offset + limit]

    # ✅ Sérialisation
    serializer = CustomUserSerializer(users, many=True, context={"request": request})

    # ✅ Gestion des champs spécifiques à afficher
    fields = request.GET.get("fields", "").split(",") if "fields" in request.GET else None

    if fields:
        # Si des champs spécifiques sont demandés, filtrer les champs dans les résultats
        data = [
            {field: user[field] for field in fields if field in user}
            for user in serializer.data
        ]
    else:
        # Si aucun champ spécifié, retourner tous les champs
        data = serializer.data

    # ✅ Formater les URLs correctement
    for user in data:
        if "profile_pics"  in user["profile_picture"]:
            profile_picture_url = user['profile_picture']
            
            user['profile_picture'] = request.build_absolute_uri(profile_picture_url)
        else :
            profile_picture_url = user['profile_picture']
            
            profile_picture_url = profile_picture_url.replace("/media/", "")
            # Si c'est une URL relative, construis l'URL absolue
            profile_picture_url = urllib.parse.unquote(profile_picture_url)
            
            user['profile_picture'] = profile_picture_url
            


    
    
    return Response({
        "total": total_users,
        "limit": limit,
        "offset": offset,
        "users": data
    })



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_profile_picture(request):
    user = request.user
    form = ProfilePictureForm(request.POST, request.FILES, instance=user)
    if form.is_valid():
        form.save()
        return Response({'status': 'success', 'profile_picture_url': user.get_profile_picture_url()})
    else:
        return Response({'status': 'error', 'errors': form.errors}, status=400)
    

class ProfilePictureUpdateView(generics.UpdateAPIView):
    """
    Vue pour mettre à jour uniquement la photo de profil
    """
    serializer_class = ProfilePictureSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_object(self):
        return self.request.user  # On récupère l'utilisateur connecté

    def put(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=self.get_object(), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, user_id):
    """Permet à l'utilisateur authentifié de s'abonner ou de se désabonner d'un autre utilisateur."""
    user = request.user  # L'utilisateur qui envoie la requête
    target_user = get_object_or_404(CustomUser, id=user_id)  # L'utilisateur à suivre

    if user == target_user:
        return Response({"error": "Vous ne pouvez pas vous abonner à vous-même."}, status=400)

    if target_user in user.following.all():
        user.following.remove(target_user)  # Désabonnement
        return Response({"message": f"Vous vous êtes désabonné de {target_user.username}."})
    else:
        user.following.add(target_user)  # Abonnement
        return Response({"message": f"Vous êtes maintenant abonné à {target_user.username}."})
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_followers_and_following(request):
    """Retourne les abonnés et les abonnements de l'utilisateur connecté."""
    user = request.user
    followers = user.followers.all()  # Ceux qui me suivent
    following = user.following.all()  # Ceux que je suis

    data = {
        "followers": CustomUserSerializer(followers, many=True).data,
        "following": CustomUserSerializer(following, many=True).data
    }
    return Response(data)

@api_view(['GET'])
def user_followers_and_following(request, user_id):
    """Retourne les abonnés et abonnements d'un utilisateur spécifique."""
    target_user = get_object_or_404(CustomUser, id=user_id)
    followers = target_user.followers.all()
    following = target_user.following.all()

    data = {
        "followers": CustomUserSerializer(followers, many=True).data,
        "following": CustomUserSerializer(following, many=True).data
    }
    return Response(data)


class ReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Permet aux utilisateurs authentifiés de signaler un beat ou un utilisateur.
        """
        user = request.user

        # Vérifie si l'utilisateur est authentifié
        if not user or not user.is_authenticated:
            return Response({"error": "Authentification requise."}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.data.copy()

        # Vérification des champs
        report_type = data.get("report_type")
        reported_user_id = data.get("reported_user")
        reported_beat_id = data.get("reported_beat")

        if report_type not in ["user", "beat"]:
            return Response({"error": "Type de signalement invalide."}, status=status.HTTP_400_BAD_REQUEST)

        if report_type == "user" and not reported_user_id:
            return Response({"error": "L'ID de l'utilisateur signalé est requis."}, status=status.HTTP_400_BAD_REQUEST)

        if report_type == "beat" and not reported_beat_id:
            return Response({"error": "L'ID du beat signalé est requis."}, status=status.HTTP_400_BAD_REQUEST)

        if report_type == "user":
            try:
                reported_user = CustomUser.objects.get(id=reported_user_id)
                data["reported_user"] = reported_user.id
            except CustomUser.DoesNotExist:
                return Response({"error": "Utilisateur introuvable."}, status=status.HTTP_404_NOT_FOUND)

        if report_type == "beat":
            try:
                reported_beat = Beat.objects.get(id=reported_beat_id)
                data["reported_beat"] = reported_beat.id
            except Beat.DoesNotExist:
                return Response({"error": "Beat introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # Passe l'utilisateur directement au serializer
        serializer = ReportSerializer(data=data, context={"request": request})

        if serializer.is_valid():
            serializer.save(reporter=user)  # Ajoute explicitement le reporter
            return Response({"message": "Signalement enregistré avec succès."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

class ReportListView(ListAPIView):
    """
    Liste les signalements pour les administrateurs.
    """
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAdminUser]


class UserNotificationsView(generics.ListAPIView):
    """
    Vue pour récupérer les notifications de l'utilisateur connecté.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notifications.objects.filter(user=self.request.user)

class AddNotificationView(APIView):
    """
    Vue pour ajouter une notification à un utilisateur.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user')
        message = request.data.get('message')

        if not user_id or not message:
            return Response({"error": "user_id et message sont requis."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"error": "Utilisateur non trouvé."}, status=status.HTTP_404_NOT_FOUND)

        notification = Notifications.objects.create(user=user, message=message)
        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class NotificationUpdateView(APIView):
    """Vue API pour mettre à jour une notification spécifique (PATCH uniquement)."""
    
    permission_classes = [IsAuthenticated]

    def patch(self, request, notification_id):
        """Met à jour partiellement une notification (ex: is_read=True)."""
        notification = get_object_or_404(Notifications, id=notification_id, user=request.user)
        serializer = NotificationSerializer(notification, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)