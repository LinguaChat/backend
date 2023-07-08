from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.db import models

from core.models import DateCreatedModel, DateEditedModel

# from django.db import models


User = get_user_model()


class Chat(DateCreatedModel, DateEditedModel):
    '''Модель чата'''
    ...


class Message(DateCreatedModel, DateEditedModel):
    """Модель для представления сообщения."""

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE
    )
    text = models.TextField(
        max_length=5000
    )
    voice_message = models.FileField(
        upload_to='voice_messages/',
        validators=[FileExtensionValidator(['mp3', 'wav'])],
        blank=True,
        null=True
    )
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
    is_pinned = models.BooleanField(
        default=False,
        verbose_name='Сообщение закреплено'
    )

    def __str__(self):
        return f"Message {self.message_id}"

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'


class MessageReaders(models.Model):
    """Модель для отслеживания прочитанных сообщений пользователем."""

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )


class Attachment(models.Model):
    """Модель для представления вложений сообщений."""

    name = models.CharField(max_length=255)
    content = models.BinaryField()
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Attachment'
        verbose_name_plural = 'Attachments'
