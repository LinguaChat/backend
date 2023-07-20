"""Файл административных настроек для приложения chats."""

from django.contrib import admin

from .models import Attachment, Chat, ChatMembers, Message, MessageReaders

admin.site.register(Chat)
admin.site.register(ChatMembers)
admin.site.register(Attachment)
admin.site.register(Message)
admin.site.register(MessageReaders)
