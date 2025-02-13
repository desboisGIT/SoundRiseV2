
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import Beat,License,BeatTrack,BeatComment,DraftBeat,Conditions
from .serializers import BeatSerializer,BeatActionSerializer,LicenseSerializer,BeatTrackSerializer,BeatCommentSerializer,ConditionsSerializer,DraftBeatSerializer
from django.db.models import Q
from core.models import CustomUser
from rest_framework import viewsets, permissions, generics
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.decorators import action
from rest_framework import viewsets, status
from django.db import transaction
import json
from rest_framework.generics import ListAPIView
from .permissions import AllowAnyGetAuthenticatedElse

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
    permission_classes = [AllowAnyGetAuthenticatedElse]

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
    http_method_names = ["get", "post", "put", "patch", "delete"]  
    permission_classes = [AllowAnyGetAuthenticatedElse]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

        

class UserLicenseListView(ListAPIView):
    serializer_class = LicenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return License.objects.filter(user=self.request.user)
    

class BeatTrackViewSet(viewsets.ModelViewSet):
    queryset = BeatTrack.objects.all()  # ✅ S'assurer que tous les objets sont récupérés
    serializer_class = BeatTrackSerializer
    permission_classes = [AllowAnyGetAuthenticatedElse]
    
from django.http import JsonResponse


class UserTracksView(APIView):
    """
    Vue pour récupérer les beats associés à un utilisateur authentifié.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Récupérer l'utilisateur authentifié
        user = request.user
        
        # Récupérer toutes les licenses de l'utilisateur
        licenses = License.objects.filter(user=user)
        
        # Récupérer tous les BeatTracks associés à ces licenses
        tracks = BeatTrack.objects.filter(licenses__in=licenses)
        
        # Sérialiser les BeatTracks
        serializer = BeatTrackSerializer(tracks, many=True)
        
        # Retourner la réponse avec les données sérialisées
        return Response(serializer.data)
    

class BeatCommentViewSet(viewsets.ModelViewSet):
    serializer_class = BeatCommentSerializer
    permission_classes = [AllowAnyGetAuthenticatedElse]

    def get_queryset(self):
        """ Récupère les commentaires d'un beat """
        beat_id = self.request.query_params.get("beat_id")
        if beat_id:
            return BeatComment.objects.filter(beat_id=beat_id)
        return BeatComment.objects.all()

    def perform_create(self, serializer):
        """ Assigner l'utilisateur connecté au commentaire """
        serializer.save(user=self.request.user)

@api_view(['GET'])
def conditions_by_license(request, license_id):
    """Retourne les conditions associées à une licence spécifique."""
    conditions = Conditions.objects.filter(licenses__id=license_id)  # Utilisation de licenses__id
    serializer = ConditionsSerializer(conditions, many=True)
    return Response(serializer.data)



class DraftBeatListCreateView(generics.ListCreateAPIView):
    """Lister tous les drafts de l'utilisateur connecté et en créer un nouveau."""
    serializer_class = DraftBeatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk=None):
        try:
            # Récupérer l'objet DraftBeat
            draft_beat = DraftBeat.objects.get(pk=pk)

            # Récupérer les données envoyées dans la requête
            title = request.data.get('title', draft_beat.title)
            bpm = request.data.get('bpm', draft_beat.bpm)
            key = request.data.get('key', draft_beat.key)
            genre = request.data.get('genre', draft_beat.genre)
            cover_image = request.data.get('cover_image', draft_beat.cover_image)
            is_public = request.data.get('is_public', draft_beat.is_public)
            co_artists_ids = request.data.get('co_artists', [])

            # Récupérer les IDs des licenses et tracks
            license_ids = request.data.get('license_ids', [])
            track_ids = request.data.get('track_ids', [])

            # Mettre à jour les champs non-relations
            draft_beat.title = title
            draft_beat.bpm = bpm
            draft_beat.key = key
            draft_beat.genre = genre
            draft_beat.cover_image = cover_image
            draft_beat.is_public = is_public

            # Ajouter les co-artists (ManyToMany relation)
            if co_artists_ids:
                co_artists = CustomUser.objects.filter(id__in=co_artists_ids)  # On suppose que co_artists est une relation avec User
                draft_beat.co_artists.add(*co_artists)

            # Ajouter les licenses au DraftBeat (ManyToMany)
            if license_ids:
                licenses = License.objects.filter(id__in=license_ids)
                draft_beat.licenses.add(*licenses)

            # Ajouter les tracks au DraftBeat (ManyToMany)
            if track_ids:
                tracks = BeatTrack.objects.filter(id__in=track_ids)
                draft_beat.tracks.add(*tracks)

            # Sauvegarder les modifications
            draft_beat.save()

            return Response({"status": "DraftBeat updated successfully"}, status=status.HTTP_200_OK)

        except DraftBeat.DoesNotExist:
            return Response({"error": "DraftBeat not found"}, status=status.HTTP_404_NOT_FOUND)

        
   
            
    
   
    def get_queryset(self):
        """Récupérer uniquement les drafts de l'utilisateur connecté."""
        return DraftBeat.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Créer un draft en liant l'utilisateur."""
        serializer.save(user=self.request.user)



class DraftBeatDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Récupérer, modifier ou supprimer un draft spécifique."""
    serializer_class = DraftBeatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Limiter l'accès aux drafts de l'utilisateur connecté."""
        return DraftBeat.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        """Supprimer un draft et retourner une réponse personnalisée."""
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Draft supprimé avec succès."}, status=status.HTTP_204_NO_CONTENT)
    







class FinalizeDraftView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, draft_id):
        """Convertir un brouillon en Beat avec Tracks et Licenses."""
        try:
            draft = DraftBeat.objects.get(id=draft_id, user=request.user)
        except DraftBeat.DoesNotExist:
            return Response({"error": "Brouillon non trouvé"}, status=status.HTTP_404_NOT_FOUND)

        licenses_data = draft.licenses.all() # Licenses envoyées dans la requête
        co_artists_data = draft.co_artists.all()  # Co-artistes envoyés dans la requête
        tracks_data = draft.tracks.all()  # Récupérer tous les tracks associés au brouillon
        user = request.user
        with transaction.atomic():
            
            # 1️⃣ **Création du Beat**
            beat_data = {
                "title": draft.title,
                "bpm": draft.bpm,
                "key": draft.key,
                "main_artist": user.id,
                "cover_image": draft.cover_image,
                "genre": draft.genre,
                "is_public": draft.is_public,
            }

            # Passer le contexte 'request' au sérialiseur
            beat_serializer = BeatActionSerializer(data=beat_data, context={'request': request})  # Passer le 'request' ici
            if not beat_serializer.is_valid():
                return Response({"errors": beat_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            beat = beat_serializer.save()

            # 2️⃣ **Association des Licenses**
            beat.licenses.set(licenses_data)  # Associer les licenses au Beat

            # 3️⃣ **Association des Co-artistes**
            beat.co_artists.set(co_artists_data)  # Associer les co-artistes au Beat

            # 4️⃣ **Association des Tracks**
            beat.tracks.set(tracks_data)  # Associer directement les tracks au Beat

            # ✅ Suppression du brouillon
            draft.delete()

            # Retourner les données du Beat créé
            return Response(BeatActionSerializer(beat, context={'request': request}).data, status=status.HTTP_201_CREATED)  # Passer le 'request' ici aussi

        return Response({"error": "Une erreur inconnue s'est produite."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class CreateConditionsView(generics.CreateAPIView):
    queryset = Conditions.objects.all()
    serializer_class = ConditionsSerializer




@api_view(['GET'])
def user_drafts(request):
    permission_classes = [IsAuthenticated]
    """Retourne les drafts de l'utilisateur connecté."""
    
    # Vérifier si l'utilisateur est authentifié
    if not request.user.is_authenticated:
        return Response({"detail": "Non authentifié."}, status=401)
    
    # Récupérer tous les drafts associés à l'utilisateur connecté
    drafts = DraftBeat.objects.filter(user=request.user)
    
    # Sérialiser les drafts
    serializer = DraftBeatSerializer(drafts, many=True)
    
    # Retourner la réponse avec les données sérialisées
    return Response(serializer.data)