from django.contrib import admin

from .models import Attachment, Chat, Message, MessageReaders

admin.site.register(Chat)
admin.site.register(Attachment)
admin.site.register(Message)
admin.site.register(MessageReaders)
