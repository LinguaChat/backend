from django.contrib import admin

from .models import Attachment, Message, MessageReaders

admin.site.register(Message)
admin.site.register(MessageReaders)
admin.site.register(Attachment)
