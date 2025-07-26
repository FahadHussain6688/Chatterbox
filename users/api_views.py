from rest_framework import generics, permissions
from .models import Status
from .serializers import StatusSerializer

class StatusListCreateAPIView(generics.ListCreateAPIView):
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
