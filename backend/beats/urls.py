from django.urls import path
from . import views

urlpatterns = [
    # Autres URLs ici...
    path('filter/', views.filter_beats, name='filter_beats'),
]
