from django.urls import path,include
from .views import RegisterView,LogoutView,VerifyEmailView,CustomTokenObtainPairView
from rest_framework_simplejwt.views import  TokenRefreshView
from . import views

app_name="authentication"
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'), 
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('', include('allauth.urls')),  
    path('social/', include('allauth.socialaccount.urls')),
    path('google/callback/', views.google_callback, name='google_callback'),

]
