from django.urls import path
from .views import get_soundkit_files

urlpatterns = [
    path("<int:soundkit_id>/files/", get_soundkit_files, name="get_soundkit_files"),
]
