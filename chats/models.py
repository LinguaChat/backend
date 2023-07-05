from django.contrib.auth import get_user_model
from django.db import models
from core.models import CreatedModifiedModel

User = get_user_model()


class Chat(CreatedModifiedModel):
    """Модель для представления чата."""

    title = models.CharField(
        max_length=255,
        unique=True
    )
    initiator = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    slug = models.SlugField(
        blank=False,
        null=False
    )
    allow_anonymous_access = models.BooleanField(
        default=False
    )
    private = models.BooleanField(
        default=False
    )
    password = models.CharField(
        max_length=200,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'


class MessageReaders(models.Model):
    """Модель для отслеживания прочитанных сообщений пользователем."""

    message = models.ForeignKey(
        'Message',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )


class Message(CreatedModifiedModel):
    """Модель для представления сообщения."""

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    chat = models.ForeignKey(
        'Chat',
        on_delete=models.CASCADE
    )
    date_sent = models.DateTimeField()
    date_edited = models.DateTimeField(
        blank=True,
        null=True
    )
    content = models.TextField()
    responding_to = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    sender_keep = models.BooleanField(
        default=False,
        verbose_name='Сообщение отправлено'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Сообщение прочитано'
    )

    def __str__(self):
        return f"Message {self.message_id}"

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
