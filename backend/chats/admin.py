from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Attachment, Chat, GroupChat, Message, PersonalChat

User = get_user_model()


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    pass


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    pass


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'chat', 'text')


@admin.register(PersonalChat)
class PersonalChatAdmin(admin.ModelAdmin):
    pass


@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    pass
