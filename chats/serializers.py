"""Сериализаторы для приложения chats."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Attachment, Chat, Message, MessageReaders

User = get_user_model()


class ChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat


class AttachmentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Attachment.

    """
    content = serializers.CharField(write_only=True)

    class Meta:
        model = Attachment
        fields = [
            'name',
            'content',
            'message'
        ]


class MessageReadersSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели MessageReaders.

    """
    class Meta:
        model = MessageReaders
        fields = [
            'message',
            'user',
        ]


class MessageSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Message.

    """
    voice_message = serializers.SerializerMethodField()
    text = serializers.CharField(allow_null=True, max_length=5000)
    # sender = UserSerializer(read_only=True)
    chat = ChatSerializer(read_only=True)
    message_readers = MessageReadersSerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'chat',
            'text',
            'voice_message',
            'responding_to',
            'sender_keep',
            'is_read',
            'is_pinned'
            'message_readers'
        ]

    def get_voice_message(self, obj: Message):
        """
        Получает URL голосового сообщения.

        """
        if obj.voice_message:
            return obj.voice_message.url
        return None
