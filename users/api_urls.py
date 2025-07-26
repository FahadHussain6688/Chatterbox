from django.urls import path
from .api_views import StatusListCreateAPIView

urlpatterns = [
    path('statuses/', StatusListCreateAPIView.as_view(), name='api_statuses'),
]
