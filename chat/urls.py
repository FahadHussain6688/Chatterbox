from django.urls import path, include
from chat import views, views_list

urlpatterns = [
    path('', views.home, name='home'),
    path('create-chat/<int:user_id>/', views.create_chat),
    path('create-chat/<str:username>/', views.create_chat_by_username),
    path('<int:chat_id>/messages/', views.get_chat_messages),
    path('<int:chat_id>/read/', views.mark_read),
    path('delete-message/<int:message_id>/', views.delete_message, name='delete_message'),
    path('delete-chat/<int:chat_id>/', views.delete_chat, name='delete_chat'),  # Updated this line
    path('users/', include('users.urls')),
    path('all-data/', views_list.all_data_view, name='all_data'),
]