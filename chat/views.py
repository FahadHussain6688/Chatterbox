from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from .models import Chat, Message # Assuming you have models for Chat and Message
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
import logging
from django.db import transaction
logger = logging.getLogger(__name__)

@login_required # Apply login_required here as this will be your main dashboard
def home(request):
    """
    This view now serves as the main dashboard, rendering room.html
    and providing all necessary context for chat list, active users,
    profile, and status sections.
    """
    # Fetch all chats for the current user
    chats = Chat.objects.filter(participants=request.user).order_by('-last_message__timestamp')

    # Fetch all other users for the "Active Users" sidebar
    other_users = User.objects.exclude(id=request.user.id)

    # Fetch statuses for the current user (assuming 'Status' is a model)
    # You'll need to import your Status model here if it's in a different app
    # For now, I'm assuming 'statuses' is an empty list or needs to be fetched from a Status model
    # from .models import Status # Uncomment and adjust if Status is in your current app
    statuses = [] # Placeholder: You'll need to fetch real statuses here, e.g., Status.objects.filter(user=request.user)


    return render(request, 'chat/room.html', {
        'chats': chats,
        'other_users': other_users,
        'statuses': statuses, # Ensure you're passing actual statuses here
        # 'room_name': None, # No longer directly needed for the default view
        # 'chat_id': None,   # No specific chat selected initially
        # 'messages': [],    # Messages are loaded via AJAX when a chat is selected
    })

# The 'room' view is now essentially redundant because its functionality
# has been absorbed by the 'home' view and the JavaScript in room.html.
# If you remove the '<str:room_name>/' URL pattern, you can delete this.
# For now, it's commented out as requested.
# @login_required
# def room(request, room_name):
#     # Show all users except the current user in the sidebar
#     users = User.objects.exclude(id=request.user.id)
#     # Find the chat for this room_name and user
#     chat = Chat.objects.filter(participants=request.user)
#     messages = []
#     chat_id = None
#     try:
#         other_user = User.objects.get(username=room_name)
#         chat = chat.filter(participants=other_user).first()
#         if chat:
#             messages = chat.messages.order_by('timestamp').values('id', 'sender__username', 'content', 'timestamp')
#             chat_id = chat.id
#     except User.DoesNotExist:
#         chat = None
#     return render(request, 'chat/room.html', {
#         'room_name': room_name,
#         'chat_id': chat_id,
#         'users': users, # Note: In the consolidated template, this is 'other_users'
#         'messages': list(messages),
#     })

@login_required # Add this decorator if not already present, as these are backend actions
def create_chat(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    existing = Chat.objects.filter(participants=request.user).filter(participants=target_user)
    if existing.exists():
        chat = existing.first()
    else:
        chat = Chat.objects.create()
        chat.participants.set([request.user, target_user])
    return JsonResponse({'chat_id': chat.id})

@login_required # Add this decorator
def create_chat_by_username(request, username):
    if not request.user.is_authenticated: # This check is redundant with @login_required, but harmless.
        return JsonResponse({'error': 'Not authenticated'}, status=403)
    try:
        target_user = User.objects.get(username=username)
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    if target_user == request.user:
        return JsonResponse({'error': 'Cannot chat with yourself'}, status=400)
    existing = Chat.objects.filter(participants=request.user).filter(participants=target_user)
    if existing.exists():
        chat = existing.first()
    else:
        chat = Chat.objects.create()
        chat.participants.set([request.user, target_user])
    return JsonResponse({'chat_id': chat.id})

@login_required # Add this decorator
def get_chat_messages(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in chat.participants.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    messages = chat.messages.all().order_by('timestamp').values('id', 'sender__username', 'content', 'timestamp', 'is_read') # Added is_read for seen indicator
    
    # Mark messages as read when fetched
    for msg in messages:
        # We need the actual Message object, not just the values dict
        message_obj = Message.objects.get(id=msg['id'])
        if request.user not in message_obj.read_by.all():
            message_obj.read_by.add(request.user)

    return JsonResponse(list(messages), safe=False)

@login_required # Add this decorator
def mark_read(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    # Ensure current user is a participant before marking read
    if request.user not in chat.participants.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Correctly mark all unread messages for the current user in this chat as read
    for msg in chat.messages.exclude(read_by=request.user):
        msg.read_by.add(request.user)
    return JsonResponse({'status': 'ok'})

@login_required # Add this decorator
def delete_message(request, message_id):
    if request.method == 'POST':
        msg = get_object_or_404(Message, id=message_id, sender=request.user)
        msg.delete()
        return JsonResponse({'status': 'deleted'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
@require_http_methods(["POST"])  # Only allow POST requests
def delete_chat(request, chat_id):
    try:
        # Use select_related/prefetch_related if you need related objects
        chat = Chat.objects.get(id=chat_id)
        
        # More efficient permission check using exists()
        if not chat.participants.filter(id=request.user.id).exists():
            raise PermissionDenied("You don't have permission to delete this chat")
            
        # Additional safety check - ensure chat has exactly 2 participants
        # (assuming this is a one-to-one chat system)
        if chat.participants.count() != 2:
            raise PermissionDenied("Invalid chat configuration")
            
        # Delete the chat and related messages in a transaction
        with transaction.atomic():
            # Delete related messages first if needed
            chat.messages.all().delete()  # Only if you want to delete messages too
            chat.delete()
            
        return JsonResponse({
            'success': True, 
            'message': 'Chat deleted successfully',
            'chat_id': chat_id  # Return the deleted chat ID for frontend reference
        })
        
    except Chat.DoesNotExist:
        return JsonResponse({
            'success': False, 
            'error': 'Chat not found'
        }, status=404)
        
    except PermissionDenied as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=403)
        
    except Exception as e:
        # Log the unexpected error for debugging
        logger.error(f"Error deleting chat {chat_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred'
        }, status=500)
