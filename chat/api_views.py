from rest_framework import generics, permissions
from .models import Chat, Message
from .serializers import ChatSerializer, MessageSerializer, ChatCreateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ChatListCreateAPIView(generics.ListCreateAPIView):
    queryset = Chat.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ChatCreateSerializer
        return ChatSerializer

    def perform_create(self, serializer):
        serializer.save()

class MessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        chat_id = self.kwargs['chat_id']
        return Message.objects.filter(chat_id=chat_id)

    def perform_create(self, serializer):
        chat_id = self.kwargs['chat_id']
        serializer.save(sender=self.request.user, chat_id=chat_id)

class DeleteChatAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id, participants=request.user)
        except Chat.DoesNotExist:
            return Response({'error': 'Chat not found or unauthorized'}, status=status.HTTP_404_NOT_FOUND)
        chat.delete()
        return Response({'status': 'deleted'}, status=status.HTTP_200_OK)
