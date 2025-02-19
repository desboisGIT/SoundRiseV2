# urls.py

from django.urls import path
from .views import ConversationListView,InvitationListView

urlpatterns = [
    path('conversations/', ConversationListView.as_view(), name='conversation-list'),
    path('invitations/', InvitationListView.as_view(), name='invitation-list'),

]
