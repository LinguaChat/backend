"""Административные настройки приложения chats."""

from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Attachment, Chat, ChatMembers, Message, MessageReaders

User = get_user_model()


class ChatMembersInline(admin.TabularInline):
    model = ChatMembers


class ChatAdmin(admin.ModelAdmin):
    inlines = [ChatMembersInline]


admin.site.register(Chat, ChatAdmin)
admin.site.register(Attachment)
admin.site.register(Message)
admin.site.register(MessageReaders)
