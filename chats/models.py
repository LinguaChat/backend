from django.contrib.auth import get_user_model
from django.db import models
from core.models import CreatedModifiedModel

User = get_user_model()


class Chat(CreatedModifiedModel):
    title = models.CharField(max_length=255, unique=True)
    initiator = models.ForeignKey(User, on_delete=models.CASCADE)
    slug = models.SlugField(blank=False, null=False)
    allow_anonymous_access = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    password = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'

