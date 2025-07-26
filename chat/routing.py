# chat/routing.py
from django.urls import re_path
from chat import consumers, presence_consumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<chat_id>\d+)/$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/presence/$', presence_consumer.PresenceConsumer.as_asgi()),
]
