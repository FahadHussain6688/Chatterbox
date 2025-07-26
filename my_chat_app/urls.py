from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from chat import views


urlpatterns = [
    path('', include('users.urls')),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('chat/', include('chat.urls')),
    path('api/users/', include('users.api_urls')),
    path('api/chat/', include('chat.api_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
