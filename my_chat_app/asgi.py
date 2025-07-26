import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_chat_app.settings')

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            __import__('chat.routing').routing.websocket_urlpatterns
        )
    ),
})
