from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from datetime import timedelta

class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def is_read_by(self, user):
        return self.read_by.filter(id=user.id).exists()

    class Meta:
        ordering = ['timestamp']
