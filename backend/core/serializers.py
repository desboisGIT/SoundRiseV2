from rest_framework import serializers
from .models import CustomUser,Report,Notifications
from beats.models import Beat
import urllib.parse

class CustomUserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    beats = serializers.SerializerMethodField()  # Ajout des beats liés à l'utilisateur

    class Meta:
        model = CustomUser
        fields = [
            "id", "username", "email", "profile_picture", "bio", "badges",
            "trending_beats", "recent_publications", "instagram", "youtube",
            "spotify", "twitter", "soundcloud", "tiktok", "apple_music",
            "website", "is_online", "beats","following","followers"  # Ajout du champ beats
        ]

    def get_profile_picture(self, obj):
        request = self.context.get("request")
        profile_picture_url = obj.profile_picture.url if obj.profile_picture else ""
        return profile_picture_url
    
    def get_beats(self, obj):
        """Retourne les beats liés à cet utilisateur en tant que main_artist"""
        beats = Beat.objects.filter(main_artist=obj)  # Filtre les beats où l'utilisateur est l'artiste principal
        return [{"id": beat.id, "title": beat.title, "created_at": beat.created_at} for beat in beats]

class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["profile_picture"]



class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = "__all__"
        read_only_fields = ["reporter"]

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = ['id', 'user', 'message', 'is_read', 'timestamp',"notif_type"]
        read_only_fields = ['created_at']
