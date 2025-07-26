from django.shortcuts import render, get_object_or_404
from chat.models import Chat, Message
from users.models import Status
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def all_data_view(request):
    # All chats for the logged-in user
    user_chats = Chat.objects.filter(participants=request.user)
    # All messages for these chats
    chat_messages = {chat.id: Message.objects.filter(chat=chat) for chat in user_chats}
    # All statuses (active, not expired)
    from django.utils import timezone
    from datetime import timedelta
    time_threshold = timezone.now() - timedelta(hours=24)
    statuses = Status.objects.filter(timestamp__gte=time_threshold)
    return render(request, 'chat/all_data.html', {
        'user_chats': user_chats,
        'chat_messages': chat_messages,
        'statuses': statuses,
    })
