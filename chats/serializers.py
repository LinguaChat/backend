"""Сериализаторы для приложения chats."""

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from .models import Chat, ChatMembers
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
            is_creator = True
        )
        ChatMembers.objects.create(
            chat=chat,
            member=companion
        )
        return chat
