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
    text = serializers.CharField(
        allow_null=True,
        max_length=5000
    )
    chat = ChatSerializer(
        read_only=True
    )
    message_readers = MessageReadersSerializer(
        many=True,
        read_only=True
    )
    file_to_send = serializers.FileField(
        write_only=True,
        required=False,
        allow_empty_file=True
    )

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'chat',
            'text',
            'file_to_send',
            'responding_to',
            'sender_keep',
            'is_read',
            'is_pinned',
            'message_readers'
        ]

    def create(self, validated_data):
        file_to_send = validated_data.pop('file_to_send', None)

        message = Message.objects.create(**validated_data)

        if file_to_send:
            Attachment.objects.create(
                name=file_to_send.name,
                content=file_to_send.read(),
                message=message
            )

        return message

    def update(self, instance, validated_data):
        file_to_send = validated_data.pop('file_to_send', None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if file_to_send:
            Attachment.objects.create(
                name=file_to_send.name,
                content=file_to_send.read(),
                message=instance
            )

        instance.save()

        return instance

