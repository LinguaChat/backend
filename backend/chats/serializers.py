"""Сериализаторы приложения chats."""

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from chats.models import Attachment, Chat, GroupChat, Message
from users.serializers import UserShortSerializer

# from rest_framework.exceptions import PermissionDenied
# from rest_framework.generics import get_object_or_404


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
        required=False,
        allow_empty_file=True
    )

    photo_to_send = serializers.ImageField(
        required=False,
        allow_empty_file=True
    )
    voice_message = serializers.FileField(
        required=False,
        allow_empty_file=True
    )
    emojis = serializers.CharField(max_length=255, required=False)

    def get_is_read(self, instance):
        user = self.context['request'].user
        return instance.read_by.filter(id=user.id).exists() and user != instance.sender

    class Meta:
        model = Message
        fields = [
            'id',
            'sender',
            'chat',
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
        ]
        extra_kwargs = {
            'chat': {'write_only': True},
        }

    def create(self, validated_data):
        file_to_send = validated_data.pop('file_to_send', None)
        photo_to_send = validated_data.pop('photo_to_send', None)
        voice_message = validated_data.pop('voice_message', None)
        emojis = validated_data.pop('emojis', None)
        text = validated_data.get('text', '')

        validated_data['sender'] = self.context['request'].user
        validated_data['sender_keep'] = True
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
        if voice_message:
            text += f" [Voice Message: {voice_message.name}]"
        if emojis:
            text += f" {emojis}"

        validated_data['text'] = text
        return message

    def update(self, instance, validated_data):
        file_to_send = validated_data.pop('file_to_send', None)
        photo_to_send = validated_data.pop('photo_to_send', None)
        voice_message = validated_data.pop('voice_message', None)
        emojis = validated_data.pop('emojis', None)
        text = validated_data.get('text', '')

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if voice_message:
            text += f" [Voice Message: {voice_message.name}]"
        if emojis:
            text += f" {emojis}"

        validated_data['text'] = text

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


class ChatListSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра списка чатов."""

    # other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = (
            'id',
            'name',
            # 'other_user',
            "last_message",
            # 'unread',
            # 'unread_messages_count',
        )
        read_only_fields = fields

    # def get_other_user(self, obj):
    #     user = self.context.get('request').user
    #     return UserProfileSerializer(
    #         *obj.members.exclude(id=user.id),
    #         context={'request': self.context.get('request')}
    #     ).data

    def get_last_message(self, obj):
        messages = obj.messages.all().order_by('-date_created')
        if not messages.exists():
            return None
        message = messages[0]
        return MessageSerializer(message).data


class ChatSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра чата."""

    messages = MessageSerializer(
        many=True,
        read_only=False
    )

    class Meta:
        model = Chat
        fields = (
            'id',
            'name',
            "messages",
        )
        read_only_fields = (
            'id',
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
