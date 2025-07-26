from rest_framework import serializers
from chat.models import Chat, Message
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    chat = serializers.PrimaryKeyRelatedField(read_only=True)
    read_by_other = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'content', 'timestamp', 'read_by_other']

    def get_read_by_other(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        # Get all participants except the sender
        participants = obj.chat.participants.exclude(id=obj.sender.id)
        # If any participant has read the message, return True
        return obj.read_by.filter(id__in=participants.values_list('id', flat=True)).exists()

class ChatSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    class Meta:
        model = Chat
        fields = ['id', 'participants', 'created_at', 'messages']

class ChatCreateSerializer(serializers.ModelSerializer):
    participants = serializers.ListField(
        child=serializers.CharField(), write_only=True
    )
    display_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Chat
        fields = ['id', 'participants', 'created_at', 'display_name']

    def get_display_name(self, obj):
        user = self.context['request'].user
        # Get the other participant's username (for 1-to-1 chat)
        others = obj.participants.exclude(id=user.id)
        if others.exists():
            return others.first().username
        return None

    def create(self, validated_data):
        usernames = validated_data.pop('participants', [])
        from django.contrib.auth.models import User
        users = list(User.objects.filter(username__in=usernames))
        if not users:
            raise serializers.ValidationError({'participants': 'No valid users found.'})
        chat = Chat.objects.create()
        chat.participants.set([self.context['request'].user] + users)
        return chat
