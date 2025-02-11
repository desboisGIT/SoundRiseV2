from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import CustomUserSerializer
from .models import CustomUser
from .forms import ProfilePictureForm
from django.db.models import Q

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
        profile_picture_url = request.build_absolute_uri(user.profile_picture.url)
        return Response({"profile_picture": profile_picture_url})
    return Response({"profile_picture": None})



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def filter_users(request):
    """
    Filtre et affiche les utilisateurs en fonction des champs et critères choisis.
    Exemple : 
        - /api/users/filter/?id=2
        - /api/users/filter/?username=John
        - /api/users/filter/?email=...,username=...
        - /api/users/filter/?bio__isnull=false&fields=username,email
    """

    queryset = CustomUser.objects.all()

    # ✅ Appliquer les filtres dynamiques sur les champs valides
    valid_fields = [field.name for field in CustomUser._meta.fields]  # Liste des champs du modèle
    filter_params = {}

    for key, value in request.GET.items():
        if key.startswith(("limit", "offset", "fields")):
            continue  # Ne pas inclure ces champs dans les filtres

        # Gestion des booléens pour isnull
        if value.lower() == "false":
            value = False
        elif value.lower() == "true":
            value = True

        if "__" in key:  # Gestion des filtres avancés (ex: bio__isnull=false)
            base_field = key.split("__")[0]
        else:
            base_field = key

        if base_field in valid_fields:
            filter_params[key] = value

    queryset = queryset.filter(**filter_params)

    # ✅ Pagination sécurisée
    try:
        limit = max(1, int(request.GET.get("limit", 10)))  # Min = 1
    except (ValueError, TypeError):
        limit = 10  # Par défaut

    try:
        offset = max(0, int(request.GET.get("offset", 0)))  # Min = 0
    except (ValueError, TypeError):
        offset = 0  # Par défaut

    total_users = queryset.count()
    users = queryset[offset : offset + limit]

    # ✅ Sérialisation
    serializer = CustomUserSerializer(users, many=True, context={"request": request})

    # ✅ Gestion des champs spécifiques à afficher
    fields = request.GET.get("fields", "").split(",") if "fields" in request.GET else None

    if fields:
        data = [
            {field: user[field] for field in fields if field in user}
            for user in serializer.data
        ]
    else:
        data = serializer.data  # Si aucun champ spécifié, on retourne tout

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