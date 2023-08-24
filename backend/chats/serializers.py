"""Сериализаторы приложения chats."""

from django.contrib.auth import get_user_model

from rest_framework import serializers

from chats.models import Attachment, GroupChat, Message, PersonalChat
from core.constants import MAX_MESSAGE_LENGTH
from users.serializers import UserShortSerializer

# from django.shortcuts import get_object_or_404
# from rest_framework.exceptions import PermissionDenied

from django.shortcuts import get_object_or_404
from .models import Chat
User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    """Сериализатор модели Message."""

    text = serializers.CharField(
        allow_null=True,
        max_length=10000
    )
    # chat = serializers.CharField(source='chat.name')
    # chat = serializers.SlugRelatedField(
    #     slug_field='name',
    #     many=False,
    #     read_only=True
    # )
    is_read = serializers.SerializerMethodField()
    read_by = UserShortSerializer(
        many=True,
        read_only=True
    )
    file_to_send = serializers.FileField(
        write_only=False,
        required=False,
        allow_empty_file=True,
        validators=[validate_file_size, validate_pdf_extension]
    )

    photo_to_send = serializers.ImageField(
        write_only=False,
        required=False,
        allow_empty_file=True,
        validators=[validate_file_size, validate_image_extension]
    )
    voice_message = serializers.FileField(
        required=False,
        allow_empty_file=True,
        validators=[validate_file_size, validate_audio_extension]
    )
    emojis = serializers.CharField(max_length=255, required=False)

    def get_is_read(self, instance):
        user = self.context['request'].user
        return (
            instance.read_by.filter(id=user.id).exists() and
            user != instance.sender
        )
    sender = serializers.SlugRelatedField(
        slug_field='slug',
        read_only=True
    )
    chat = serializers.HiddenField(default=None)

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'text',
            'file_to_send',
            'photo_to_send',
            'voice_message',
            'emojis',
            'responding_to',
            'sender_keep',
            'is_read',
            'is_pinned',
            'read_by',
            'timestamp',
            'chat',
        ]
        extra_kwargs = {
            'chat': {'write_only': True},
        }
        read_only_fields = (
            'id',
            'sender',
            'sender_keep',
            'is_read',
            'is_pinned',
            'read_by',
            'timestamp',
        )

    # def create(self, validated_data):
    #     file_to_send = validated_data.get('file_to_send', None)
    #     photo_to_send = validated_data.get('photo_to_send', None)
    #     voice_message = validated_data.get('voice_message', None)
    #     emojis = validated_data.get('emojis', None)
    #     text = validated_data.get('text', '')

    #     validated_data['sender'] = self.context['request'].user
    #     validated_data['sender_keep'] = True

    #     if voice_message:
    #         text = f'[Voice Message: {voice_message.name}]'
    #     if emojis:
    #         text += emojis

    #     message = Message.objects.create(**validated_data)

    def create(self, validated_data):
        file_to_send = validated_data.get('file_to_send', None)
        photo_to_send = validated_data.get('photo_to_send', None)
        voice_message = validated_data.get('voice_message', None)
        emojis = validated_data.get('emojis', None)
        text = validated_data.get('text', '')
        chatname = validated_data['chat']

        validated_data['sender_keep'] = True

        chat = get_object_or_404(Chat, name=chatname)

        if not chat.messages.exists() and (file_to_send or photo_to_send):
            raise serializers.ValidationError(
                "Нельзя отправить фото или файл первым сообщением"
            )
        if voice_message:
            text = f'[Voice Message: {voice_message.name}]'
        if emojis:
            text += emojis
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

        message.text = text
        return message

    def update(self, instance, validated_data):
        file_to_send = validated_data.get('file_to_send', None)
        photo_to_send = validated_data.get('photo_to_send', None)
        voice_message = validated_data.get('voice_message', None)
        emojis = validated_data.get('emojis', None)
        text = validated_data.get('text', '')
        # return message

    # def update(self, instance, validated_data):
    #     file_to_send = validated_data.pop('file_to_send', None)
    #     photo_to_send = validated_data.pop('photo_to_send', None)

    #     for key, value in validated_data.items():
    #         setattr(instance, key, value)

        if voice_message:
            text = f'[Voice Message: {voice_message.name}]'
        if emojis:
            text += emojis

        instance.text = text

        if file_to_send:
            Attachment.objects.create(
                name=file_to_send.name,
                content=file_to_send.read(),
                message=instance
            )
    #     if file_to_send:
    #         Attachment.objects.create(
    #             name=file_to_send.name,
    #             content=file_to_send.read(),
    #             message=instance
    #         )

        if photo_to_send:
            Attachment.objects.create(
                name=photo_to_send.name,
                content=photo_to_send.read(),
                message=instance
            )

        instance.save()

        return instance


class ChatListSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра списка чатов."""

    initiator = UserShortSerializer(many=False, read_only=True)
    receiver = UserShortSerializer(many=False, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread = serializers.SerializerMethodField()

    class Meta:
        model = PersonalChat
        fields = (
            'id',
            'initiator',
            'receiver',
            "last_message",
            'unread',
        )
        read_only_fields = fields

    def get_last_message(self, obj):
        message = obj.messages.first()
        return MessageSerializer(message).data

    def get_unread(self, obj):
        return obj.messages.filter(read_by=None).count()


class ChatSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра чата."""

    initiator = UserShortSerializer(many=False, read_only=True)
    receiver = UserShortSerializer(many=False, read_only=True)
    messages = MessageSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = PersonalChat
        fields = (
            'id',
            'initiator',
            'receiver',
            "messages",
        )
        read_only_fields = (
            'id',
            'initiator',
            'receiver',
            "messages",
        )


class ChatStartSerializer(serializers.ModelSerializer):
    """Сериализатор для создания личного чата."""

    receiver = serializers.SlugRelatedField(
        slug_field='slug',
        read_only=False,
        queryset=User.objects.all()
    )
    message = serializers.CharField(
        max_length=MAX_MESSAGE_LENGTH,
        required=True
    )

    class Meta:
        model = PersonalChat
        fields = (
            'receiver',
            "message",
        )


class GroupChatCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания группового чата."""

    members = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=User.objects.all(),
        many=True
    )

    class Meta:
        model = GroupChat
        fields = (
            'name',
            "members",
        )

    # def to_representation(self, instance):
    #     return ChatReprSerializer(
    #         instance,
    #         context={'request': self.context.get('request')}
    #     ).data

    # def create(self, validated_data):
    #     chat = Chat.objects.create(**validated_data)
    #     # ChatMembers.objects.create(
    #     #     chat=chat,
    #     #     member=creator,
    #     #     is_creator=True
    #     # )
    #     # ChatMembers.objects.create(
    #     #     chat=chat,
    #     #     member=companion
    #     # )
    #     return chat


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
