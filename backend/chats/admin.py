"""Административные настройки приложения chats."""

from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Attachment, Chat, GroupChat, Message, PersonalChat

User = get_user_model()


class ChatAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_members_count', 'get_blocked_users')
    filter_horizontal = ('members', 'blocked_users')

    def get_blocked_users(self, obj):
        return ", ".join([str(user) for user in obj.blocked_users.all()])

    get_blocked_users.short_description = 'Заблокированные участники'


admin.site.register(Chat, ChatAdmin)
admin.site.register(Attachment)
admin.site.register(Message)
admin.site.register(PersonalChat)
admin.site.register(GroupChat)
