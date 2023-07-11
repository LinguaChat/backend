"""Сериализаторы для приложения chats."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Chat

User = get_user_model()


class ChatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Chat
