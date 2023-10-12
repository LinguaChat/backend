from django.contrib import admin

from .models import Attachment, Chat, GroupChat, Message, PersonalChat


class ChatAdmin(admin.ModelAdmin):
    filter_horizontal = ('blocked_users',)

    def get_name(self, obj):
        return str(obj)

    get_name.short_description = 'Имя'

    def get_blocked_users(self, obj):
        return ", ".join([str(user) for user in obj.blocked_users.all()])

    get_blocked_users.short_description = 'Заблокированные участники'

    def initiator(self, obj):
        return obj.initiator

    initiator.short_description = 'Инициатор'
    initiator.admin_order_field = 'initiator'


class PersonalChatAdmin(ChatAdmin):
    list_display = ('id', 'get_name', 'get_blocked_users',
                    'initiator', 'receiver', 'date_created')


class GroupChatAdmin(ChatAdmin):
    list_display = ('id', 'get_name', 'get_blocked_users',
                    'initiator', 'display_members', 'date_created')

    def display_members(self, obj):
        return ", ".join([str(user) for user in obj.members.all()])

    display_members.short_description = 'Участники'

    
admin.site.register(Chat, ChatAdmin)
admin.site.register(Attachment)
admin.site.register(Message)
admin.site.register(PersonalChat, PersonalChatAdmin)
admin.site.register(GroupChat, GroupChatAdmin)
