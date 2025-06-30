from django.urls import path
from .views import ChatConversationView

urlpatterns = [
    path('conversation/<str:symbol_name>/', ChatConversationView.as_view(), name='chat-conversation'),
]