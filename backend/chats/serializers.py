"""Сериализаторы приложения chats."""

from django.contrib.auth import get_user_model

from rest_framework import serializers
# from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404

from chats.models import Attachment, Chat, ChatMembers, Message, MessageReaders
from users.serializers import UserSerializer

User = get_user_model()


class ChatListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка чатов."""

    companion = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = (
            'id',
            'companion',
            # 'latest_message',
            # 'unread',
            # 'unread_messages_count',
        )

    def get_companion(self, obj):
        user = self.context.get('request').user
        return UserSerializer(
            *obj.members.exclude(id=user.id),
            context={'request': self.context.get('request')}
        ).data


class ChatReprSerializer(ChatListSerializer):
    """Сериализатор для просмотра чата."""

    class Meta:
        model = Chat
        fields = (
            'id',
            'companion',
            # 'messages',
        )


class ChatSerializer(serializers.ModelSerializer):
    """Сериализатор для создания чата."""

    companion = serializers.SlugField()

    class Meta:
        model = Chat
        fields = (
            'companion',
        )

    def to_representation(self, instance):
        return ChatReprSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data

    def create(self, validated_data):
        companion_slug = validated_data.pop("companion", None)
        companion = get_object_or_404(User, slug=companion_slug)
        creator = self.context.get('request').user

        # if companion.chats.filter(members__in=creator).exists():
        #     return PermissionDenied(
        #         'Чат с этим пользователем уже создан.'
        #     )

        chat = Chat.objects.create(**validated_data)
        ChatMembers.objects.create(
            chat=chat,
            member=creator,
            is_creator=True
        )
        ChatMembers.objects.create(
            chat=chat,
            member=companion
        )
        return chat


class AttachmentSerializer(serializers.ModelSerializer):
    """Сериализатор модели Attachment."""

    content = serializers.CharField(write_only=True)

    class Meta:
        model = Attachment
        fields = [
            'name',
            'content',
            'message'
        ]


class MessageReadersSerializer(serializers.ModelSerializer):
    """Сериализатор модели MessageReaders."""

    class Meta:
        model = MessageReaders
        fields = [
            'message',
            'user',
        ]


class MessageSerializer(serializers.ModelSerializer):
    """Сериализатор модели Message."""

    text = serializers.CharField(
        allow_null=True,
        max_length=10000
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
    photo_to_send = serializers.ImageField(
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
            'photo_to_send',
            'responding_to',
            'sender_keep',
            'is_read',
            'is_pinned',
            'message_readers'
        ]

    def create(self, validated_data):
        file_to_send = validated_data.pop('file_to_send', None)
        photo_to_send = validated_data.pop('photo_to_send', None)
        chat = validated_data['chat']

        if not chat.messages.exists() and (file_to_send or photo_to_send):
            raise serializers.ValidationError(
                "Нельзя отправить фото или файл первым сообщением"
            )

        validated_data['sender'] = self.context['request'].user
        message = Message.objects.create(**validated_data)

        if file_to_send:
            Attachment.objects.create(
                name=file_to_send.name,
                content=file_to_send.read(),
                message=message
            )

        if photo_to_send:
            Attachment.objects.create(
                name=photo_to_send.name,
                content=photo_to_send.read(),
                message=message
            )

        return message

    def update(self, instance, validated_data):
        file_to_send = validated_data.pop('file_to_send', None)
        photo_to_send = validated_data.pop('photo_to_send', None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if file_to_send:
            Attachment.objects.create(
                name=file_to_send.name,
                content=file_to_send.read(),
                message=instance
            )

        if photo_to_send:
            Attachment.objects.create(
                name=photo_to_send.name,
                content=photo_to_send.read(),
                message=instance
            )

        instance.save()

        return instance
