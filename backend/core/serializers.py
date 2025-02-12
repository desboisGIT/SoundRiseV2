from rest_framework import serializers
from .models import CustomUser  # Assure-toi que c'est le bon chemin
import urllib.parse

class CustomUserSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "profile_picture","bio","is_online"]  

class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["profile_picture"]

