from rest_framework import serializers
from .models import CustomUser  # Assure-toi que c'est le bon chemin
import urllib.parse

class CustomUserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "profile_picture","bio","is_online"]  
    
    def get_profile_picture(self, obj):
        if obj.profile_picture:
            path = obj.profile_picture.url.replace("/media/", "")
            return urllib.parse.unquote(path)  # Décodage ici
        return None

