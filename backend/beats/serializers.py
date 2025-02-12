from rest_framework import serializers
from .models import Beat, License, BeatTrack

class BeatSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)  # Afficher l'ID de l'utilisateur
    user = serializers.CharField(source='user.username', read_only=True)  # Afficher le username de l'utilisateur
    likes = serializers.SerializerMethodField()  # Personnaliser la sérialisation des likes
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    def get_likes(self, obj):
        # Retourner les usernames des utilisateurs qui ont aimé le beat
        return [user.username for user in obj.likes.all()]

    class Meta:
        model = Beat
        fields = ['id', 'title', 'audio_file', 'cover_image', 'bpm', 'key', 'genre', 'price'
                  , 'likes_count', 'created_at', 'updated_at', 'user', 'user_id', 'likes',"is_liked","is_favorited"]
    def get_is_liked(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and obj.likes.filter(id=user.id).exists()

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        return user.is_authenticated and obj.favorites.filter(id=user.id).exists()



class BeatTrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = BeatTrack
        fields = "__all__"



class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = ['id', 'title', 'price', 'description', 'beat']


class BeatActionSerializer(serializers.ModelSerializer):
    licenses = LicenseSerializer(many=True, read_only=True)  # Récupérer les licences associées
    tracks = BeatTrackSerializer(many=True, read_only=True)  # Récupérer les pistes audio associées
    is_liked = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Beat
        fields = "__all__"
        extra_kwargs = {
            'main_artist': {'required': False}  # Désactive l'obligation d'envoyer main_artist
        }
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
