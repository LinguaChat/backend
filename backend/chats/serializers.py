"""Сериализаторы приложения chats."""

from django.contrib.auth import get_user_model

from rest_framework import serializers

from chats.models import GroupChat, Message, PersonalChat
from core.constants import MAX_MESSAGE_LENGTH
from users.serializers import UserShortSerializer

# from django.shortcuts import get_object_or_404

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    """Сериализатор модели Message."""

    text = serializers.CharField(
        allow_null=True,
        max_length=10000
    )
    read_by = UserShortSerializer(
        many=True,
        read_only=True
    )
    file_to_send = serializers.FileField(
        write_only=False,
        required=False,
        allow_empty_file=True
    )
    photo_to_send = serializers.ImageField(
        write_only=False,
        required=False,
        allow_empty_file=True
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
    #     file_to_send = validated_data.pop('file_to_send', None)
    #     photo_to_send = validated_data.pop('photo_to_send', None)
        # chatname = validated_data['chat']
        # chat = get_object_or_404(Chat, name=chatname)

        # if not chat.messages.exists() and (file_to_send or photo_to_send):
        #     raise serializers.ValidationError(
        #         "Нельзя отправить фото или файл первым сообщением"
        #     )

        # validated_data['sender'] = self.context['request'].user
        # message = Message.objects.create(**validated_data)

        # if file_to_send:
        #     Attachment.objects.create(
        #         name=file_to_send.name,
        #         content=file_to_send.read(),
        #         message=message
        #     )

        # if photo_to_send:
        #     Attachment.objects.create(
        #         name=photo_to_send.name,
        #         content=photo_to_send.read(),
        #         message=message
        #     )

        # return message

    # def update(self, instance, validated_data):
    #     file_to_send = validated_data.pop('file_to_send', None)
    #     photo_to_send = validated_data.pop('photo_to_send', None)

    #     for key, value in validated_data.items():
    #         setattr(instance, key, value)

    #     if file_to_send:
    #         Attachment.objects.create(
    #             name=file_to_send.name,
    #             content=file_to_send.read(),
    #             message=instance
    #         )

    #     if photo_to_send:
    #         Attachment.objects.create(
    #             name=photo_to_send.name,
    #             content=photo_to_send.read(),
    #             message=instance
    #         )

    #     instance.save()

    #     return instance


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
    blocked_users = serializers.StringRelatedField(
        many=True
    )

    class Meta:
        model = PersonalChat
        fields = (
            'id',
            'initiator',
            'receiver',
            "messages",
            "blocked_users",
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
