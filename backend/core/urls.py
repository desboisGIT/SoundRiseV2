from django.urls import path, include
from . import views 
from .views import update_profile_picture,ProfilePictureUpdateView

urlpatterns = [
    path('oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path("user/", views.get_user_profile, name="user-profile"),
    path("users/filter/", views.filter_users, name="filter-users"),
    path('user/update-profile-picture/', update_profile_picture, name='update_profile_picture'),
    path('user/profile_picture/', views.get_profile_picture, name='get_profile_picture'),
    path("user/upload/profile-picture/", ProfilePictureUpdateView.as_view(), name="profile-picture-update"),
]