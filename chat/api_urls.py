from django.urls import path
from .api_views import ChatListCreateAPIView, MessageListCreateAPIView, DeleteChatAPIView

urlpatterns = [
    path('chats/', ChatListCreateAPIView.as_view(), name='api_chats'),
    path('chats/<int:chat_id>/messages/', MessageListCreateAPIView.as_view(), name='api_chat_messages'),
    path('chats/<int:chat_id>/delete/', DeleteChatAPIView.as_view(), name='api_chat_delete'),
]
