
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






class CheckDraftCompletenessView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, draft_id):
        """Vérifie si un brouillon est complet avant finalisation."""
        try:
            draft = DraftBeat.objects.get(id=draft_id, user=request.user)
        except DraftBeat.DoesNotExist:
            return Response({"error": "Brouillon non trouvé"}, status=status.HTTP_404_NOT_FOUND)

        missing_fields = []

        # Vérification des champs obligatoires
        required_fields = ["title", "bpm", "key", "cover_image", "genre"]
        for field in required_fields:
            if not getattr(draft, field, None):
                missing_fields.append(field)

        # Vérification des tracks
        if not isinstance(draft.tracks, list) or len(draft.tracks) == 0:
            missing_fields.append("tracks (au moins un est requis)")
        else:
            for i, track in enumerate(draft.tracks, start=1):
                if not isinstance(track, dict):
                    missing_fields.append(f"track {i} : format invalide")
                else:
                    if "title" not in track or not track["title"]:
                        missing_fields.append(f"track {i} : 'title' manquant")
                    if "audio_file" not in track or not track["audio_file"]:
                        missing_fields.append(f"track {i} : 'audio_file' manquant")

        # Vérification des licenses
        if not isinstance(draft.licenses, list) or len(draft.licenses) == 0:
            missing_fields.append("licenses (au moins une est requise)")
        else:
            for i, license in enumerate(draft.licenses, start=1):
                if not isinstance(license, dict):
                    missing_fields.append(f"license {i} : format invalide")
                else:
                    if "title" not in license or not license["title"]:
                        missing_fields.append(f"license {i} : 'title' manquant")
                    if "price" not in license or not isinstance(license["price"], (int, float)):
                        missing_fields.append(f"license {i} : 'price' manquant ou invalide")

                    # Vérification des conditions dans chaque license
                    if "conditions" not in license or not isinstance(license["conditions"], list) or len(license["conditions"]) == 0:
                        missing_fields.append(f"license {i} : 'conditions' (au moins une est requise)")
                    else:
                        for j, condition in enumerate(license["conditions"], start=1):
                            if not isinstance(condition, dict):
                                missing_fields.append(f"license {i}, condition {j} : format invalide")
                            else:
                                if "title" not in condition or not condition["title"]:
                                    missing_fields.append(f"license {i}, condition {j} : 'title' manquant")
                                if "value" not in condition:
                                    missing_fields.append(f"license {i}, condition {j} : 'value' manquant")
                                if "description" not in condition or not condition["description"]:
                                    missing_fields.append(f"license {i}, condition {j} : 'description' manquant")

        # Si tout est complet
        if not missing_fields:
            return Response({"message": "Le brouillon est complet et prêt à être finalisé."}, status=status.HTTP_200_OK)

        # Retourner la liste des champs manquants
        return Response({"missing_fields": missing_fields}, status=status.HTTP_400_BAD_REQUEST)





class FinalizeDraftView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, draft_id):
        """Convertir un brouillon en Beat, Conditions, Licenses et Tracks."""
        errors = {}

        try:
            draft = DraftBeat.objects.get(id=draft_id, user=request.user)
        except DraftBeat.DoesNotExist:
            return Response({"error": "Brouillon non trouvé"}, status=status.HTTP_404_NOT_FOUND)

        # Extraction des données
        tracks_data = draft.tracks
        licenses_data = draft.licenses
        conditions_data = draft.conditions
        beat_data = {
            "title": draft.title,
            "bpm": draft.bpm,
            "key": draft.key,
            "main_artist": request.user,
            "co_artists": draft.co_artists,
            "cover_image": draft.cover_image,
            "genre": draft.genre,
            "is_public": draft.is_public,
        }

        try:
            with transaction.atomic():
                # 1️⃣ Création des Tracks
                created_tracks = []
                tracks_errors = []
                for track_data in tracks_data:
                    track_serializer = BeatTrackSerializer(data=track_data)
                    if track_serializer.is_valid():
                        track = track_serializer.save()
                        created_tracks.append(track)
                    else:
                        tracks_errors.append(track_serializer.errors)
                
                if tracks_errors:
                    errors["tracks"] = tracks_errors

                # 2️⃣ Création des Conditions
                created_conditions = []
                conditions_errors = []
                for condition_data in conditions_data:
                    condition_serializer = ConditionsSerializer(data=condition_data)
                    if condition_serializer.is_valid():
                        condition = condition_serializer.save()
                        created_conditions.append(condition)
                    else:
                        conditions_errors.append(condition_serializer.errors)
                
                if conditions_errors:
                    errors["conditions"] = conditions_errors

                # 3️⃣ Création des Licenses
                created_licenses = []
                licenses_errors = []
                for license_data in licenses_data:
                    track_ids = license_data.pop("tracks", [])
                    conditions_ids = license_data.pop("conditions", [])

                    license_serializer = LicenseSerializer(data=license_data)
                    if license_serializer.is_valid():
                        license_obj = license_serializer.save()

                        # Associer les Tracks à la License
                        linked_tracks = BeatTrack.objects.filter(id__in=track_ids)
                        license_obj.tracks.set(linked_tracks)

                        # Associer les Conditions à la License
                        linked_conditions = Conditions.objects.filter(id__in=conditions_ids)
                        license_obj.conditions.set(linked_conditions)

                        created_licenses.append(license_obj)
                    else:
                        licenses_errors.append(license_serializer.errors)
                
                if licenses_errors:
                    errors["licenses"] = licenses_errors

                # 🎵 4️⃣ Création du Beat
                beat_serializer = BeatActionSerializer(data=beat_data)
                if beat_serializer.is_valid():
                    beat = beat_serializer.save()
                    beat.licenses.set(created_licenses)
                else:
                    errors["beat"] = beat_serializer.errors

                # 🔥 Vérifier si des erreurs existent
                if errors:
                    return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

                # Supprimer le brouillon
                draft.delete()

                return Response(BeatActionSerializer(beat).data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"Une erreur inattendue s'est produite: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def conditions_by_license(request, license_id):
    """Retourne les conditions associées à une licence spécifique."""
    conditions = Conditions.objects.filter(license_id=license_id)
    serializer = ConditionsSerializer(conditions, many=True)
    return Response(serializer.data)



class DraftBeatListCreateView(generics.ListCreateAPIView):
    """Lister tous les drafts de l'utilisateur connecté et en créer un nouveau."""
    serializer_class = DraftBeatSerializer
    permission_classes = [permissions.IsAuthenticated]

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