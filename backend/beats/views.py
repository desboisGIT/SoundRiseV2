
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from .models import Beat,License,BeatComment,DraftBeat,Hashtag,BeatView
from .serializers import BeatSerializer,BeatActionSerializer,LicenseSerializer,BeatCommentSerializer,DraftBeatSerializer,HashtagSerializer
from django.db.models import Q
from core.models import CustomUser
from rest_framework import viewsets, permissions, generics
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.decorators import action
from rest_framework import viewsets, status
from django.db import transaction
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.exceptions import ValidationError 
from django.db import IntegrityError  
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

    # 🔹 Filtrage par hashtags
    hashtags = request.GET.get("hashtags", None)
    if hashtags:
        hashtag_names = [h.strip().lower() for h in hashtags.split(",")]
        queryset = queryset.filter(hashtags__name__in=hashtag_names).distinct()

        
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
    """
    Vue pour récupérer la liste des licences associées à l'utilisateur authentifié.
    Ajout du filtrage des champs et de la pagination.
    """

    serializer_class = LicenseSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination  # Utilisation correcte de la pagination

    def get_queryset(self):
        return License.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Appliquer la pagination correctement
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
        else:
            serializer = self.get_serializer(queryset, many=True)

        # Gestion du filtrage des champs
        fields_param = request.query_params.get("fields")
        if fields_param:
            requested_fields = set(fields_param.split(","))

            # Obtenir les champs valides du serializer
            serializer_instance = self.get_serializer()
            allowed_fields = set(serializer_instance.fields.keys())

            valid_fields = requested_fields & allowed_fields

            if not valid_fields:
                raise ValidationError({"error": "Aucun champ valide spécifié."})

            serialized_data = [
                {field: item[field] for field in valid_fields} for item in serializer.data
            ]
        else:
            serialized_data = serializer.data

        # Retour des données paginées avec les champs sélectionnés
        return self.get_paginated_response(serialized_data) if page is not None else Response(serialized_data)

    

    





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
    try:
        # Trouver la licence avec l'id spécifique
        license = License.objects.get(id=license_id)  # Utilisation de `get()` pour obtenir un seul objet License
        conditions = license.conditions.all()  # Accéder aux conditions associées à cette licence
        serializer = ConditionsSerializer(conditions, many=True)  # Sérialiser les conditions
        return Response(serializer.data)
    except License.DoesNotExist:
        return Response({"detail": "License not found."}, status=status.HTTP_404_NOT_FOUND)




class DraftBeatListCreateView(generics.ListCreateAPIView):
    """Lister tous les drafts de l'utilisateur connecté et en créer un nouveau."""
    serializer_class = DraftBeatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtrer les drafts de l'utilisateur connecté
        return DraftBeat.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        """Créer un nouveau brouillon avec l'utilisateur connecté comme créateur."""
        # Assigner l'utilisateur connecté (request.user) lors de la création
        data = request.data.copy()
        data['user'] = request.user.id  # Assigner l'utilisateur automatiquement

        # Utiliser le sérialiseur pour valider et enregistrer
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            draft_beat = serializer.save()  # Sauvegarder le brouillon
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        """Mettre à jour un brouillon spécifique."""
        try:
            # Récupérer l'objet DraftBeat
            draft_beat = DraftBeat.objects.get(pk=pk, user=request.user)

            # Récupérer les données envoyées dans la requête
            title = request.data.get('title', draft_beat.title)
            bpm = request.data.get('bpm', draft_beat.bpm)
            key = request.data.get('key', draft_beat.key)
            genre = request.data.get('genre', draft_beat.genre)
            cover_image = request.data.get('cover_image', draft_beat.cover_image)
            co_artists_ids = request.data.get('co_artists', [])

            # Récupérer les IDs des licenses 
            license_ids = request.data.get('license_ids', [])

            # Mettre à jour les champs non-relations
            draft_beat.title = title
            draft_beat.bpm = bpm
            draft_beat.key = key
            draft_beat.genre = genre
            draft_beat.cover_image = cover_image

            # Ajouter les co-artists (ManyToMany relation)
            if co_artists_ids:
                co_artists = CustomUser.objects.filter(id__in=co_artists_ids)
                draft_beat.co_artists.set(co_artists)

            # Ajouter les licenses au DraftBeat (ManyToMany)
            if license_ids:
                licenses = License.objects.filter(id__in=license_ids)
                draft_beat.licenses.set(licenses)

            # Sauvegarder les modifications
            draft_beat.save()

            return Response({"status": "DraftBeat updated successfully"}, status=status.HTTP_200_OK)

        except DraftBeat.DoesNotExist:
            return Response({"error": "DraftBeat not found or user unauthorized"}, status=status.HTTP_404_NOT_FOUND)




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
    






from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import transaction
from .models import DraftBeat, Beat
from .serializers import BeatActionSerializer

class FinalizeDraftView(APIView):
    permission_classes = [IsAuthenticated]

    def get_required_audio_formats(self, licenses):
        """
        Retourne les formats audio requis en fonction des types de fichiers associés aux licences.
        """
        all_formats = ['mp3', 'wav', 'flac', 'ogg', 'aac', 'alac', 'zip']  # Pas de '.' ici
        license_file_types = set()

        for license in licenses:
            print(f"License: {license}, Types de fichiers: {license.license_file_types}")

            if isinstance(license.license_file_types, list):
                license_file_types.update(license.license_file_types)
            else:
                license_file_types.add(license.license_file_types)

        print(f"License File Types: {license_file_types}")

        # Trouver les formats requis en enlevant le '.' dans all_formats pour correspondre avec license_file_types
        required_formats = [format for format in all_formats if format in license_file_types]

        print(f"Required Formats: {required_formats}")

        return required_formats


    def post(self, request, draft_id):
        """Convertir un brouillon en Beat avec Licenses."""
        try:
            draft = DraftBeat.objects.get(id=draft_id, user=request.user)
        except DraftBeat.DoesNotExist:
            return Response({"error": "Brouillon non trouvé"}, status=status.HTTP_404_NOT_FOUND)

        licenses_data = draft.licenses.all()
        co_artists_data = draft.co_artists.all()
        user = request.user

        # Gérer les formats audio requis en fonction des licences
        required_formats = self.get_required_audio_formats(licenses_data)

        # Vérifier si les formats audio requis sont présents et non nuls dans le brouillon (draft)
        missing_formats = [
            format for format in required_formats 
            if not getattr(draft, format.lstrip('.'), None)  # Si le fichier est None ou vide
        ]
        if missing_formats:
            return Response(
                {"error": f"Les formats audio suivants sont manquants : {', '.join(missing_formats)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Vérifier les formats de fichiers audio dans request.FILES
        allowed_formats = required_formats + [".mp3", ".wav", ".flac", ".ogg", ".aac", ".alac", ".zip"]
        for format_key, file in request.FILES.items():
            file_extension = file.name.split('.')[-1].lower()  # Extraire l'extension du fichier
            if f".{file_extension}" not in allowed_formats:
                return Response(
                    {"error": f"Le format de fichier '{file.name}' n'est pas autorisé. Les formats valides sont : {', '.join(allowed_formats)}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Si tout est valide, procéder à la création du Beat
        beat_data = {
            "title": draft.title,
            "bpm": draft.bpm,
            "key": draft.key,
            "main_artist": user.id,
            "cover_image": draft.cover_image,
            "genre": draft.genre,
            "hashtags": [],  # Les hashtags seront ajoutés plus bas
        }

        # Ajouter les fichiers audio requis dans le beat_data
        for format in required_formats:
            format_key = format.lstrip('.')  # Retirer le point pour avoir une clé valide
            if hasattr(draft, format) and getattr(draft, format):  # Vérifier si le fichier est présent et non nul
                beat_data[format_key] = getattr(draft, format)

        # Création du Beat via le sérialiseur
        beat_serializer = BeatActionSerializer(data=beat_data, context={'request': request})
        if not beat_serializer.is_valid():
            return Response({"errors": beat_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        beat = beat_serializer.save()

        # Association des Licenses, Co-artistes et Hashtags
        beat.licenses.set(licenses_data)
        beat.co_artists.set(co_artists_data)
        beat.hashtags.set([])  # Si des hashtags sont ajoutés plus bas, les ajouter ici.

        # Suppression du brouillon
        draft.delete()

        return Response(BeatActionSerializer(beat, context={'request': request}).data, status=status.HTTP_201_CREATED)




    





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


class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = [AllowAnyGetAuthenticatedElse]



def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


class AddBeatView(APIView):
    def post(self, request, beat_id):
        """Ajoute une vue à un Beat si l'utilisateur ou l'IP ne l'a pas encore vu"""
        try:
            beat = Beat.objects.get(id=beat_id)
        except Beat.DoesNotExist:
            return Response({"error": "Beat non trouvé"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user if request.user.is_authenticated else None
        ip_address = get_client_ip(request) if user is None else None  # On stocke l'IP si l'user n'est pas connecté

        # Vérifier si la vue existe déjà
        if user:
            exists = BeatView.objects.filter(beat=beat, user=user).exists()
        else:
            exists = BeatView.objects.filter(beat=beat, ip_address=ip_address).exists()

        if exists:
            return Response({"message": "Vue déjà enregistrée"}, status=status.HTTP_200_OK)

        # Ajouter la nouvelle vue
        try:
            BeatView.objects.create(beat=beat, user=user, ip_address=ip_address)
            return Response({"message": "Vue ajoutée avec succès"}, status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response({"message": "Vue déjà existante"}, status=status.HTTP_200_OK)
        
class GetBeatViews(APIView):
    def get(self, request, beat_id):
        try:
            beat = Beat.objects.get(id=beat_id)
            return Response({"total_views": beat.total_views}, status=status.HTTP_200_OK)
        except Beat.DoesNotExist:
            return Response({"error": "Beat non trouvé"}, status=status.HTTP_404_NOT_FOUND)