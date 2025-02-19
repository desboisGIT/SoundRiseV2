from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .models import Soundkit

@api_view(["GET"])
def get_soundkit_files(request, soundkit_id):
    """Retourne la liste des fichiers contenus dans un Soundkit donné"""
    soundkit = get_object_or_404(Soundkit, id=soundkit_id)
    file_list = soundkit.extract_file_list()  # Appelle la méthode du modèle
    return Response({"soundkit": soundkit.title, "files": file_list})
