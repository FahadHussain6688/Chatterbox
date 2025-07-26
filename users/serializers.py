from rest_framework import serializers
from .models import Status
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class StatusSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Status
        fields = ['id', 'user', 'image', 'timestamp']
