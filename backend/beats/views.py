
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Beat,License,BeatTrack,BeatComment
from .serializers import BeatSerializer,BeatActionSerializer,LicenseSerializer,BeatTrackSerializer,BeatCommentSerializer
from django.db.models import Q
from core.models import CustomUser
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.decorators import action
from rest_framework import viewsets, status


@api_view(['GET'])
def filter_beats(request):
    """
    Filtre et affiche les beats en fonction des critères et champs choisis, avec tri.
    Exemple : 
        - /api/beats/filter/?title=Trap&genre=Hip-Hop
        - /api/beats/filter/?title=Trap&order=price,-created_at
        - /api/beats/filter/?search=trap&order=price
        - /api/beats/filter/?user=SKorfa  # Filtrer par username
        - /api/beats/filter/?user=32     # Filtrer par ID utilisateur
    """
    
    queryset = Beat.objects.all()

    # ✅ Appliquer les filtres dynamiques sur les champs valides
    valid_fields = [field.name for field in Beat._meta.fields]  # Liste des champs du modèle Beat
    filter_params = {}

    # Appliquer les filtres de recherche
    for key, value in request.GET.items():
        if key.startswith(("limit", "offset", "fields", "order")):
            continue  # Ne pas inclure ces champs dans les filtres

        if value.lower() == "false":
            value = False
        elif value.lower() == "true":
            value = True

        if "__" in key:  # Gestion des filtres avancés (ex: genre__icontains=...)
            base_field = key.split("__")[0]
        else:
            base_field = key

        if base_field in valid_fields:
            filter_params[key] = value

    # Filtrage par 'user' (par username ou ID)
    user = request.GET.get('user', None)
    if user:
        # Si 'user' est un nombre (ID), on le convertit en entier et filtrer par ID
        if user.isdigit():
            user = int(user)
            queryset = queryset.filter(user_id=user)
        else:
            try:
                # Sinon, on cherche par username
                user = CustomUser.objects.get(username=user)
                queryset = queryset.filter(user_id=user.id)
            except CustomUser.DoesNotExist:
                return Response({"error": "User not found"}, status=404)

    # Filtrage par 'search' sur le title et le user
    search = request.GET.get('search', None)
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(user__username__icontains=search)
        )

    # Appliquer les filtres spécifiques
    queryset = queryset.filter(**filter_params)

    # ✅ Tri des résultats
    order_param = request.GET.get("order", "")
    if order_param:
        order_fields = order_param.split(",")  # Support pour tri multi-champs
        queryset = queryset.order_by(*order_fields)

    # ✅ Pagination sécurisée
    try:
        limit = max(1, int(request.GET.get("limit", 10)))  # Min = 1
    except (ValueError, TypeError):
        limit = 10  # Par défaut

    try:
        offset = max(0, int(request.GET.get("offset", 0)))  # Min = 0
    except (ValueError, TypeError):
        offset = 0  # Par défaut

    total_beats = queryset.count()
    beats = queryset[offset : offset + limit]

    # ✅ Sérialisation
    serializer = BeatSerializer(beats, many=True, context={"request": request})

    # ✅ Gestion des champs spécifiques à afficher
    fields = request.GET.get("fields", "").split(",") if "fields" in request.GET else None

    if fields:
        # Si des champs spécifiques sont demandés, on filtre les données avant de les renvoyer
        data = [
            {field: beat[field] for field in fields if field in beat}
            for beat in serializer.data
        ]
    else:
        data = serializer.data  # Si aucun champ spécifié, on retourne tout

    

    return Response({
        "total": total_beats,
        "limit": limit,
        "offset": offset,
        "beats": data
    })


class BeatViewSet(viewsets.ModelViewSet):
    """
    API pour gérer les Beats.
    """
    queryset = Beat.objects.all()
    serializer_class = BeatActionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(main_artist=self.request.user)  # Associe le beat à l'utilisateur connecté
    
    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        beat = self.get_object()
        user = request.user
        if beat.likes.filter(id=user.id).exists():
            beat.likes.remove(user)
            return Response({"message": "Like removed"}, status=status.HTTP_200_OK)
        beat.likes.add(user)
        return Response({"message": "Liked"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def favorite(self, request, pk=None):
        beat = self.get_object()
        user = request.user
        if beat.favorites.filter(id=user.id).exists():
            beat.favorites.remove(user)
            return Response({"message": "Removed from favorites"}, status=status.HTTP_200_OK)
        beat.favorites.add(user)
        return Response({"message": "Added to favorites"}, status=status.HTTP_201_CREATED)


class LicenseViewSet(viewsets.ModelViewSet):
    """
    API pour gérer les Licenses.
    """
    queryset = License.objects.all()
    serializer_class = LicenseSerializer
    http_method_names = ["get", "post", "put", "patch", "delete"]  # Vérifie bien que "post" est là !
    permission_classes = [AllowAny]
    

class BeatTrackViewSet(viewsets.ModelViewSet):
    queryset = BeatTrack.objects.all()  # ✅ S'assurer que tous les objets sont récupérés
    serializer_class = BeatTrackSerializer
    permission_classes = [AllowAny]
    
from django.http import JsonResponse


class BeatCommentViewSet(viewsets.ModelViewSet):
    serializer_class = BeatCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """ Récupère les commentaires d'un beat """
        beat_id = self.request.query_params.get("beat_id")
        if beat_id:
            return BeatComment.objects.filter(beat_id=beat_id)
        return BeatComment.objects.all()

    def perform_create(self, serializer):
        """ Assigner l'utilisateur connecté au commentaire """
        serializer.save(user=self.request.user)