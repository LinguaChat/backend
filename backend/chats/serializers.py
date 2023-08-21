"""Сериализаторы приложения chats."""

from django.contrib.auth import get_user_model

from rest_framework import serializers

from chats.models import Attachment, Chat, GroupChat, Message
from users.serializers import UserShortSerializer

# from django.shortcuts import get_object_or_404
# from rest_framework.exceptions import PermissionDenied

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
    read_by = UserShortSerializer(
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
            'read_by',
        ]
        extra_kwargs = {
            'chat': {'write_only': True},
        }

    def create(self, validated_data):
        file_to_send = validated_data.pop('file_to_send', None)
        photo_to_send = validated_data.pop('photo_to_send', None)
        # chatname = validated_data['chat']
        # chat = get_object_or_404(Chat, name=chatname)

        # if not chat.messages.exists() and (file_to_send or photo_to_send):
        #     raise serializers.ValidationError(
        #         "Нельзя отправить фото или файл первым сообщением"
        #     )

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
    blocked_users = serializers.StringRelatedField(
        many=True
    )

    class Meta:
        model = Chat
        fields = (
            'id',
            'name',
            "messages",
            "blocked_users",
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
