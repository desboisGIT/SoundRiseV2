from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from .views import BeatViewSet, LicenseViewSet, BeatCommentViewSet,FinalizeDraftView,DraftBeatListCreateView,DraftBeatDetailView,UserLicenseListView,user_drafts,AddBeatView,GetBeatViews,BundleUserListCreateAPIView,BundlePublicListAPIView,BundleUserRetrieveUpdateDestroyAPIView
router = DefaultRouter()
router.register(r"beats", BeatViewSet)


urlpatterns = [
    # Autres URLs ici...
    path('filter/', views.filter_beats, name='filter_beats'),
    path("<int:beat_id>/add_view/", AddBeatView.as_view(), name="add_beat_view"),
    path('<int:beat_id>/views/', GetBeatViews.as_view(), name='get_beat_views'),   # Récupérer le nombre de vues
    

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

    path("licenses/user/", UserLicenseListView.as_view(), name="user-licenses"),



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
    
    path('drafts/', DraftBeatListCreateView.as_view(), name='draft-list-create'),
    path('drafts/user/', user_drafts, name='user_drafts'),
    path('drafts/<int:pk>/', DraftBeatDetailView.as_view(), name='draft-detail'),
    path('draftbeats/<int:pk>/', DraftBeatListCreateView.as_view(), name='add-licenses'),
    path('finalize-draft/<int:draft_id>/', FinalizeDraftView.as_view(), name='finalize-draft'),

    path('conditions/<int:license_id>/', views.conditions_by_license, name='conditions-by-license'),

    path("bundles/user/", BundleUserListCreateAPIView.as_view(), name="bundle-user-list-create"),
    path("bundles/user/<int:pk>/", BundleUserRetrieveUpdateDestroyAPIView.as_view(), name="bundle-user-detail"),
    path("bundles/filter/", BundlePublicListAPIView.as_view(), name="bundle-public-list"),
    

]

