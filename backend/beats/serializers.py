from rest_framework import serializers
from .models import Beat, License,BeatComment,DraftBeat,Hashtag,Bundle,BundleBeat

class BeatSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)  # Afficher l'ID de l'utilisateur
    user = serializers.CharField(source='user.username', read_only=True)  # Afficher le username de l'utilisateur
    likes = serializers.SerializerMethodField()  # Personnaliser la sérialisation des likes
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    hashtags = serializers.SlugRelatedField(
        many=True, queryset=Hashtag.objects.all(), slug_field="name"
    )

    def get_likes(self, obj):
        # Retourner les usernames des utilisateurs qui ont aimé le beat
        return [user.username for user in obj.likes.all()]

    class Meta:
        model = Beat
        fields = ['id', 'title', 'audio_file', 'cover_image', 'bpm', 'key', 'genre',"hashtags", 'price'
                  , 'likes_count', 'created_at', 'updated_at', 'user', 'user_id', 'likes',"is_liked","is_favorited","view_count"]
    def get_is_liked(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and obj.likes.filter(id=user.id).exists()

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and obj.favorites.filter(id=user.id).exists()
    
    def create(self, validated_data):
        hashtag_names = validated_data.pop("hashtag_names", [])
        beat = Beat.objects.create(**validated_data)

        # Ajouter les hashtags existants ou les créer
        for name in hashtag_names:
            hashtag, created = Hashtag.objects.get_or_create(name=name.lower())
            beat.hashtags.add(hashtag)

        return beat


class LicenseSerializer(serializers.ModelSerializer):
    license_file_types = serializers.ListField(child=serializers.CharField())
    class Meta:
        model = License
        fields = ['id', 'title', 'price', 'description', 'is_exclusive', 'created_at' ,"conditions","license_template","license_file_types","terms_text"]
        read_only_fields = ["user"]
    
    def to_representation(self, instance):
        """Convertit la chaîne en liste lors de la lecture de l'API."""
        data = super().to_representation(instance)
        if isinstance(instance.license_file_types, str):
            data["license_file_types"] = instance.license_file_types.split(",")
        return data

    def validate_license_file_types(self, value):
        """Convertit la liste en chaîne avant de l'enregistrer."""
        if isinstance(value, list):
            return ",".join(value)
        return value


class BeatActionSerializer(serializers.ModelSerializer):
    licenses = LicenseSerializer(many=True, read_only=True)  # Récupérer les licences associées
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Beat
        fields = "__all__"
        extra_kwargs = {
            'main_artist': {'required': False},
            'audio_file': {'required': False, 'read_only': True},  # Assurez-vous que 'audio_file' n'est pas requis
            'audio_file': {'required': False, 'read_only': True},
        }

    def validate_title(self, value):
        """ Validation conditionnelle du champ title. """
        if not value:
            raise serializers.ValidationError("Le titre ne peut pas être vide.")
        return value

    def create(self, validated_data):
        request = self.context['request']
        validated_data['main_artist'] = request.user  # Associe l'utilisateur connecté
        return super().create(validated_data)
    
    def get_is_liked(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and obj.likes.filter(id=user.id).exists()

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and obj.favorites.filter(id=user.id).exists()

    
    

class BeatCommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")  # Ajout du nom de l'utilisateur

    class Meta:
        model = BeatComment
        fields = ["id", "beat", "user", "username", "content", "created_at"]
        read_only_fields = ["id", "user", "created_at"]  # L'utilisateur et la date sont en lecture seule

    def create(self, validated_data):
        """ Associer l'utilisateur connecté au commentaire """
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["user"] = request.user
        return super().create(validated_data)



    

class DraftBeatSerializer(serializers.ModelSerializer):
    licenses = serializers.PrimaryKeyRelatedField(queryset=License.objects.all(), many=True)
    hashtag_names = serializers.ListField(child=serializers.CharField(), required=False)  # Ajout des hashtags sous forme de liste de noms

    class Meta:
        model = DraftBeat
        fields = '__all__'

    def create(self, validated_data):
        print(validated_data)  # Débug : voir quelles données sont reçues

        # Extraire les informations supplémentaires avant de créer l'objet
        hashtag_names = validated_data.pop("hashtag_names", [])
        hashtags_data = validated_data.pop("hashtags", [])
        licenses_data = validated_data.pop("licenses", [])  # Retirer licenses s'il existe
        co_artists_data = validated_data.pop("co_artists", [])  # Retirer co_artists s'il existe

        # Créer l'objet DraftBeat sans ManyToMany et sans fichiers audio
        draft = DraftBeat.objects.create(**validated_data)

        # Ajouter les hashtags
        if hashtag_names:
            hashtags = [Hashtag.objects.get_or_create(name=name.lower())[0] for name in hashtag_names]
            draft.hashtags.add(*hashtags)

        if hashtags_data:
            draft.hashtags.add(*hashtags_data)

        # Ajouter les licenses
        if licenses_data:
            draft.licenses.set(licenses_data)

        # Ajouter les co-artistes
        if co_artists_data:
            draft.co_artists.set(co_artists_data)

        # Gérer l'ajout des fichiers audio
        audio_formats = ['mp3', 'wav', 'flac', 'ogg', 'aac', 'alac', 'zip']
        for format in audio_formats:
            if format in validated_data:
                setattr(draft, format, validated_data[format])  # Associer le fichier audio au bon champ
        draft.save()  # Sauvegarder les modifications après avoir ajouté les fichiers audio

        return draft


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ["id", "name"]


class BundleUserSerializer(serializers.ModelSerializer):
    """ Sérialiseur pour la gestion des bundles de l'utilisateur connecté """
    beats = serializers.ListField(
        child=serializers.DictField(), write_only=True
    )  # Ex: [{"beat": 1, "selected_license": 2}, {"beat": 3, "selected_license": 5}]

    bundle_beats = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Bundle
        fields = ["id", "title", "description", "price", "created_at", "beats", "bundle_beats"]

    def get_bundle_beats(self, obj):
        """ Retourne les beats et leurs licences associées """
        return [
            {
                "id": bb.id,
                "beat_id": bb.beat.id,
                "beat_title": bb.beat.title,
                "selected_license_id": bb.selected_license.id,
                "license_title": bb.selected_license.title
            }
            for bb in obj.bundle_beats.all()
        ]

    def create(self, validated_data):
        """ Création d'un bundle avec ses beats et licences """
        beats_data = validated_data.pop("beats", [])
        bundle = Bundle.objects.create(**validated_data, user=self.context["request"].user)

        for beat_data in beats_data:
            beat = Beat.objects.get(id=beat_data["beat"])
            selected_license = License.objects.get(id=beat_data["selected_license"])
            BundleBeat.objects.create(bundle=bundle, beat=beat, selected_license=selected_license)

        return bundle

    def update(self, instance, validated_data):
        """ Mise à jour d'un bundle avec suppression et ajout des beats """
        beats_data = validated_data.pop("beats", None)
        instance.title = validated_data.get("title", instance.title)
        instance.description = validated_data.get("description", instance.description)
        instance.price = validated_data.get("price", instance.price)
        instance.save()

        if beats_data is not None:
            instance.bundle_beats.all().delete()  # Supprime les anciens liens
            for beat_data in beats_data:
                beat = Beat.objects.get(id=beat_data["beat"])
                selected_license = License.objects.get(id=beat_data["selected_license"])
                BundleBeat.objects.create(bundle=instance, beat=beat, selected_license=selected_license)

        return instance
    

class BundleBeatSerializer(serializers.ModelSerializer):
    beat_title = serializers.CharField(source="beat.title", read_only=True)
    license_title = serializers.CharField(source="selected_license.title", read_only=True)
    files = serializers.SerializerMethodField()

    class Meta:
        model = BundleBeat
        fields = ["beat_title", "license_title", "files"]

    def get_files(self, obj):
        """ Récupère les fichiers associés au beat en fonction de la licence sélectionnée """
        required_files = obj.selected_license.license_file_types  # Types de fichiers exigés par la licence

        # Dictionnaire des fichiers disponibles dans Beat
        beat_files = {
            "mp3": obj.beat.mp3.url if obj.beat.mp3 else None,
            "wav": obj.beat.wav.url if obj.beat.wav else None,
            "flac": obj.beat.flac.url if obj.beat.flac else None,
            "ogg": obj.beat.ogg.url if obj.beat.ogg else None,
            "aac": obj.beat.aac.url if obj.beat.aac else None,
            "alac": obj.beat.alac.url if obj.beat.alac else None,
            "zip": obj.beat.zip.url if obj.beat.zip else None,
        }

        # Filtrer les fichiers selon les types requis par la licence et supprimer les None
        return {ftype: beat_files[ftype] for ftype in required_files if ftype in beat_files and beat_files[ftype]}


class BundlePublicSerializer(serializers.ModelSerializer):
    
    """ Sérialiseur pour afficher les bundles disponibles publiquement """
    user = serializers.StringRelatedField(read_only=True)  # Affiche le nom du créateur
    bundle_beats = BundleBeatSerializer(many=True, read_only=True)

    class Meta:
        model = Bundle
        fields = ["id", "title", "description", "price", "user", "created_at", "bundle_beats"]

    def get_bundle_beats(self, obj):
        """ Liste les beats et licences associées à ce bundle """
        return [
            {
                "beat_id": bb.beat.id,
                "beat_title": bb.beat.title,
                "license_title": bb.selected_license.title
            }
            for bb in obj.bundle_beats.all()
        ]
    


