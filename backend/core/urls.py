from django.urls import path, include
from . import views 

urlpatterns = [
    path('oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path("user/", views.get_user_profile, name="user-profile"),
    path("users/filter/", views.filter_users, name="filter-users"),
    
]