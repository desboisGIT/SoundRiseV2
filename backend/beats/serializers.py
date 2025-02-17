from rest_framework import serializers
from .models import Beat, License, BeatTrack,BeatComment,Conditions,DraftBeat,Hashtag

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
                  , 'likes_count', 'created_at', 'updated_at', 'user', 'user_id', 'likes',"is_liked","is_favorited"]
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



class BeatTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeatTrack
        fields = "__all__"



class LicenseSerializer(serializers.ModelSerializer):
    license_file_types = serializers.ListField(child=serializers.CharField())
    class Meta:
        model = License
        fields = ['id', 'title', 'price', 'description', 'is_exclusive', 'created_at' ,"conditions","license_template","license_file_types","terms_text","tracks"]
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
    tracks = BeatTrackSerializer(many=True, read_only=True)  # Récupérer les pistes audio associées
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


class ConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conditions
        fields = ['id', 'title', 'value', 'is_unlimited', 'description', 'created_at']

    def to_representation(self, instance):
        """Personnalise la sortie pour afficher 'Illimité' si is_unlimited est True."""
        data = super().to_representation(instance)
        if instance.is_unlimited:
            data['value'] = "Illimité"
        return data
    

class DraftBeatSerializer(serializers.ModelSerializer):
    tracks = serializers.PrimaryKeyRelatedField(queryset=BeatTrack.objects.all(), many=True)
    licenses = serializers.PrimaryKeyRelatedField(queryset=License.objects.all(), many=True)

    class Meta:
        model = DraftBeat
        fields = '__all__'

    def create(self, validated_data):
        hashtag_names = validated_data.pop("hashtag_names", [])
        draft = DraftBeat.objects.create(**validated_data)

        # Ajouter les hashtags existants ou les créer
        for name in hashtag_names:
            hashtag, created = Hashtag.objects.get_or_create(name=name.lower())
            draft.hashtags.add(hashtag)

        return draft


class ConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conditions
        fields = ['id', 'title', 'value', 'is_unlimited', 'description', 'created_at']


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ["id", "name"]
