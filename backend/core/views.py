from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomUserSerializer
from .models import CustomUser

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Retourne les infos de l'utilisateur connecté"""
    user = request.user
    serializer = CustomUserSerializer(user, context={"request": request})  # Ajoute `request` pour l'URL complète
    return Response(serializer.data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])  # L'utilisateur doit être connecté
def get_profile_picture(request):
    user = request.user
    if user.profile_picture:
        profile_picture_url = request.build_absolute_uri(user.profile_picture.url)
        return Response({"profile_picture": profile_picture_url})
    return Response({"profile_picture": None})



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def filter_users(request):
    """
    Filtre et affiche les utilisateurs en fonction des champs et critères choisis.
    
    """
    queryset = CustomUser.objects.all()

    # 🔹 Appliquer les filtres dynamiques (ex: bio__isnull=false, username__icontains=John)
    filter_params = {key: value for key, value in request.GET.items() if not key.startswith(("limit", "offset", "fields"))}
    queryset = queryset.filter(**filter_params)

    # 🔹 Pagination
    try:
        limit = max(1, int(request.GET.get("limit", 10)))  # Min = 1
    except (ValueError, TypeError):
        limit = 10  # Valeur par défaut

    try:
        offset = max(0, int(request.GET.get("offset", 0)))  # Min = 0
    except (ValueError, TypeError):
        offset = 0  # Valeur par défaut

    total_users = queryset.count()
    users = queryset[offset:offset + limit]

    # 🔹 Sérialisation
    serializer = CustomUserSerializer(users, many=True, context={"request": request})

    # 🔹 Sélection des champs à afficher
    fields = request.GET.get("fields", "").split(",") if "fields" in request.GET else None

    if fields:
        data = [{field: user[field] for field in fields if field in user} for user in serializer.data]
    else:
        data = serializer.data  # Si aucun champ n'est spécifié, on retourne tout

    return Response({
        "total": total_users,
        "limit": limit,
        "offset": offset,
        "users": data
    })