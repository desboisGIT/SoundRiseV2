from django.urls import path,include
from .views import RegisterView,LogoutView,VerifyEmailView,CustomTokenObtainPairView, GoogleLoginView, CustomTokenRefreshView,RequestPasswordResetView,PasswordResetConfirmView
from rest_framework_simplejwt.views import  TokenRefreshView
from . import views
from . import testing_views



app_name="authentication"

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'), 
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),  
    path('social/', include('allauth.socialaccount.urls')),
    path('google/login/', GoogleLoginView.as_view(), name='google_login'),
    path('google/callback/', views.google_callback, name='google_callback'),  # Callback
    

    path('password-reset/', RequestPasswordResetView.as_view(), name='password_reset'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),


    # Tests:
    path('test/echo-cookies/', testing_views.EchoCookiesView.as_view(), name='echo-cookies')
]






