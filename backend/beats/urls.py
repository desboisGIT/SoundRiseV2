from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from .views import BeatViewSet, LicenseViewSet, BeatTrackViewSet, BeatCommentViewSet
router = DefaultRouter()
router.register(r"beats", BeatViewSet)
urlpatterns = [
    # Autres URLs ici...
    path('filter/', views.filter_beats, name='filter_beats'),
    

    path('licenses/', LicenseViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='get_licenses'),
    path('licenses/<int:pk>/', LicenseViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='license_detail'),


    path('tracks/', BeatTrackViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='get_tracks'),
    path('tracks/<int:pk>/', BeatTrackViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='track_detail'),


    path('', BeatViewSet.as_view({
        'get': 'list',
        'post': 'create',
    }), name='get_beats'),
    path('<int:pk>/', BeatViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='beat_detail'),

    path('<int:pk>/like/', BeatViewSet.as_view({'post': 'like'}), name='like_beat'),
    path('<int:pk>/favorite/', BeatViewSet.as_view({'post': 'favorite'}), name='favorite_beat'),

    path("comments/", BeatCommentViewSet.as_view({"get": "list", "post": "create"}), name="get_comments"),
    path("comments/<int:pk>/", BeatCommentViewSet.as_view({
        "get": "retrieve",
        "put": "update",
        "patch": "partial_update",
        "delete": "destroy"
    }), name="comment_detail"),
]

