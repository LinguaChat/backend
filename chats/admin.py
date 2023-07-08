from django.contrib import admin
from .models import Chat, Message, MessageReaders, Attachment, Members

admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(MessageReaders)
admin.site.register(Attachment)
admin.site.register(Members)
