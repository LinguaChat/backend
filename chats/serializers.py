"""Сериализаторы для приложения chats."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Chat

User = get_user_model()


class ChatSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    # members = UserSerializer()

    class Meta:
        model = Chat
        fields = (
            'slug', 'title', 'owner', 'is_private', 'allow_anonymous_access',
            'members', 'image'
        )
