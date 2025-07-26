import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f'chat_{self.chat_id}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        # Broadcast online status
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'username': self.scope["user"].username,
                'user_id': self.scope["user"].id,
                'status': 'online',
            }
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        # Broadcast offline status
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'username': self.scope["user"].username,
                'user_id': self.scope["user"].id,
                'status': 'offline',
            }
        )

    async def receive(self, text_data):
        if not self.scope["user"].is_authenticated:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Not authenticated. Please log in again.'}))
            return
        
        data = json.loads(text_data)
        
        if data.get('type') == 'typing':
            user_id = self.scope["user"].id
            print(f"[DEBUG] Typing event received from user_id={user_id}, username={self.scope['user'].username}")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'username': self.scope["user"].username,
                    'user_id': user_id,
                }
            )
            return
            
        if data.get('type') == 'read':
            user_id = self.scope["user"].id
            message_ids = data.get('message_ids', [])
            print(f"[DEBUG] Received read event from user_id={user_id}, message_ids={message_ids}")
            
            # Mark messages as read and get updated message IDs
            updated_ids = await self.mark_messages_read(user_id, message_ids)
            print(f"[DEBUG] Updated IDs to broadcast: {updated_ids}")
            
            # Broadcast read receipt to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'read_receipt',
                    'user_id': user_id,
                    'username': self.scope["user"].username,
                    'message_ids': updated_ids,
                    'timestamp': str(timezone.now())
                }
            )
            return
            
        if data.get('type') == 'chat_message':
            message = data.get('message')
            if not message:
                return
                
            user_id = self.scope["user"].id
            msg_obj = await self.save_message(user_id, self.chat_id, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': msg_obj['username'],
                    'user_id': user_id,
                    'id': msg_obj['id'],
                    'chat_id': self.chat_id,
                    'is_read': False  # New messages start as unread
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat',
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'message_id': event['id'],
            'chat_id': event['chat_id'],
            'is_read': event.get('is_read', False)
        }))

    async def typing_indicator(self, event):
        # Only send to other users, not the sender
        if self.scope["user"].id != event['user_id']:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'username': event['username'],
                'user_id': event['user_id'],
            }))

    async def user_status(self, event):
        # Only send to other users, not the sender
        if self.scope["user"].id != event['user_id']:
            await self.send(text_data=json.dumps({
                'type': 'user_status',
                'username': event['username'],
                'user_id': event['user_id'],
                'status': event['status'],
            }))

    async def read_receipt(self, event):
        # Send to all users in the chat
        await self.send(text_data=json.dumps({
            'type': 'read_receipt',
            'username': event['username'],
            'user_id': event['user_id'],
            'message_ids': event['message_ids'],
            'timestamp': event.get('timestamp')
        }))

    @database_sync_to_async
    def save_message(self, user_id, chat_id, message):
        from django.contrib.auth.models import User
        from .models import Chat, Message
        user = User.objects.get(id=user_id)
        chat = Chat.objects.get(id=chat_id)
        msg = Message.objects.create(chat=chat, sender=user, content=message)
        return {
            'username': user.username,
            'id': msg.id
        }

    @database_sync_to_async
    def mark_messages_read(self, user_id, message_ids):
        from django.contrib.auth.models import User
        from .models import Message
        from django.utils import timezone

        try:
            user = User.objects.get(id=user_id)
            valid_ids = [int(mid) for mid in message_ids if str(mid).isdigit()]
            
            messages = Message.objects.filter(
                id__in=valid_ids
            ).exclude(read_by=user)
            
            updated_ids = []
            for message in messages:
                message.read_by.add(user)
                if not message.read_at:
                    message.read_at = timezone.now()
                    message.save()
                updated_ids.append(message.id)
                
            return updated_ids
        except Exception as e:
            print(f"Error marking messages read: {e}")
            return []