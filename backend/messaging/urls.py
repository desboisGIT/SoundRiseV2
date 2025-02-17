# urls.py

from django.urls import path
from .views import SendInvitationView, AcceptInvitationView

urlpatterns = [
    path('send-invitation/', SendInvitationView.as_view(), name='send-invitation'),
    path('accept-invitation/<int:invitation_id>/', AcceptInvitationView.as_view(), name='accept-invitation'),
]
