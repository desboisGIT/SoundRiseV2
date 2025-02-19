from rest_framework import serializers
from .models import Soundkit

class SoundkitSerializer(serializers.ModelSerializer):
    file_list = serializers.SerializerMethodField()  # Champ calculé pour la liste des fichiers

    class Meta:
        model = Soundkit
        fields = ["id", "title", "description", "zip_file", "creator", "created_at", "file_list"]

    def get_file_list(self, obj):
        """Retourne la liste des fichiers contenus dans le ZIP du Soundkit"""
        return obj.extract_file_list()  # Appelle la méthode du modèle
