from django.urls import path, include
from . import views 
from .views import update_profile_picture,ProfilePictureUpdateView,follow_user,my_followers_and_following,user_followers_and_following,ReportView,ReportListView

urlpatterns = [
    path('oauth/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path("user/", views.get_user_profile, name="user-profile"),
    path("users/filter/", views.filter_users, name="filter-users"),
    path('user/update-profile-picture/', update_profile_picture, name='update_profile_picture'),
    path('user/profile_picture/', views.get_profile_picture, name='get_profile_picture'),
    path("user/upload/profile-picture/", ProfilePictureUpdateView.as_view(), name="profile-picture-update"),
    path('user/follow/<int:user_id>/', follow_user, name='follow_user'),
    path('user/me/follows/', my_followers_and_following, name='my_followers_and_following'),
    path('user/<int:user_id>/follows/', user_followers_and_following, name='user_followers_and_following'),
    path("user/report/", ReportView.as_view(), name="report"),
    path("user/admin/reports/", ReportListView.as_view(), name="admin-reports"),
]