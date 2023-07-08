from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Chat, Message

User = get_user_model()


class ChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = (
            'id',
            'sender',
            'chat',
            'text',
            'voice_message',
            'responding_to',
            'sender_keep',
            'is_read',
            'is_pinned'
        )
