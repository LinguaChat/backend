"""Конфигурация приложения chats."""

from django.apps import AppConfig


class ChatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chats'
    verbose_name = 'Приложение для описания чатов и сообщений'
