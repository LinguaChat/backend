"""Файл административных настроек для приложения chats."""

from django.contrib import admin

from .models import Chat, ChatMembers

admin.site.register(Chat)
admin.site.register(ChatMembers)
