from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Attachment, Chat, GroupChat, Message, PersonalChat

User = get_user_model()


class ChatAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_members_count',
                    'get_blocked_users', 'creator')
    filter_horizontal = ('members', 'blocked_users')

    def get_blocked_users(self, obj):
        return ", ".join([str(user) for user in obj.blocked_users.all()])

    get_blocked_users.short_description = 'Заблокированные участники'

    def creator(self, obj):
        return obj.creator

    creator.short_description = 'Создатель'
    creator.admin_order_field = 'creator'


admin.site.register(Chat, ChatAdmin)
admin.site.register(Attachment)
admin.site.register(Message)
admin.site.register(PersonalChat)
admin.site.register(GroupChat)
