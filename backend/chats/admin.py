"""Административные настройки приложения chats."""

from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Attachment, Chat, PersonalChat, GroupChat, Message

User = get_user_model()


admin.site.register(Chat)
admin.site.register(Attachment)
admin.site.register(Message)
admin.site.register(PersonalChat)
admin.site.register(GroupChat)
