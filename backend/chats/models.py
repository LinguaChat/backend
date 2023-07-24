"""Модели для приложения chats."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from core.models import DateCreatedModel, DateEditedModel

User = get_user_model()


class Chat(DateCreatedModel, DateEditedModel):
    """Модель чата."""

    members = models.ManyToManyField(
        User,
        through='ChatMembers',
        verbose_name='Участники',
        help_text='Кто может просматривать и отправлять сообщения в чате',
        related_name='chats'
    )
    is_active = models.BooleanField(
        default=False,
        verbose_name='Активен ли чат',
        help_text='Собеседник ответил пользователю',
    )

    def __str__(self) -> str:
        if self.members.count() == 2:
            return (
                f'Чат пользователей {self.members.all()[0]} и '
                f'{self.members.all()[1]}'
            )
        return 'Пустой чат'

    class Meta:
        ordering = ['-date_created']
        get_latest_by = 'date_created'
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'


class ChatMembers(DateCreatedModel):
    """Модель участников чата."""

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='members_info',
        verbose_name='Чат',
        help_text='Чат, в котором участвует пользователь',
    )
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chats_info',
        verbose_name='Участник чата',
        help_text='Может просматривать и отправлять сообщения в чате'
    )
    chat_is_pinned = models.BooleanField(
        default=False,
        verbose_name='Закреплён ли чат',
        help_text='Пользователь закрепил этот чат для себя'
    )
    chat_is_cleared = models.BooleanField(
        default=False,
        verbose_name='Очищен ли чат',
        help_text='Удалены все сообщения в чате пользователем'
    )
    is_creator = models.BooleanField(
        default=False,
        verbose_name='Является ли создателем чата',
        help_text='Этот пользователь начал переписку в чате'
    )

    def __str__(self) -> str:
        chatmembers_string = (
            f'Пользователь {self.member} - участник чата {self.chat}'
        )
        if self.chat_is_pinned:
            chatmembers_string += ' (чат закреплён)'
        return chatmembers_string

    class Meta:
        ordering = ['-date_created']
        get_latest_by = 'date_created'
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'
        constraints = [
            models.UniqueConstraint(
                fields=['chat', 'member'],
                name='уникальные участники'
            )
        ]


class Message(DateCreatedModel, DateEditedModel):
    """Модель сообщения."""

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Отправитель сообщения',
        help_text='Отправитель сообщения'
    )
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        verbose_name='Чат',
        help_text='Чат, к которому относится сообщение',
        related_name='messages'
    )
    text = models.TextField(
        max_length=10000,
        verbose_name='Текст сообщения',
        help_text='Текст сообщения'
    )
    file_to_send = models.FileField(
        upload_to='files_to_send/',
        blank=True,
        null=True,
        verbose_name='Файл для отправки',
        help_text='Файл для отправки'
    )
    photo_to_send = models.ImageField(
        upload_to='photos_to_send/',
        blank=True,
        null=True,
        verbose_name='Фото для отправки',
        help_text='Фото для отправки'
    )
    responding_to = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Ответ на другое сообщение',
        help_text='Ответ на другое сообщение'
    )
    sender_keep = models.BooleanField(
        default=False,
        verbose_name='Сообщение отправлено',
        help_text='Сообщение отправлено'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Сообщение прочитано',
        help_text='Сообщение прочитано'
    )
    is_pinned = models.BooleanField(
        default=False,
        verbose_name='Сообщение закреплено',
        help_text='Сообщение закреплено'
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            chat_messages_count = Message.objects.filter(
                chat=self.chat
            ).count()
            if chat_messages_count == 0:
                if self.file_to_send or self.photo_to_send:
                    raise ValidationError(
                        "Нельзя отправить фото или файл первым сообщением"
                    )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message {self.id}"

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        constraints = [
            models.UniqueConstraint(
                fields=['text', 'sender', 'chat'],
                name='уникальное сообщение'
            )
        ]


class MessageReaders(models.Model):
    """Модель для отслеживания прочитанных пользователями сообщений."""

    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        verbose_name='Сообщение',
        help_text='Сообщение, которое было прочитано'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        help_text='Пользователь, который прочитал сообщение'
    )

    class Meta:
        verbose_name = 'Читатель сообщения'
        verbose_name_plural = 'Читатели сообщений'


class Attachment(models.Model):
    """Модель для вложений сообщений."""

    name = models.CharField(
        max_length=255,
        verbose_name='Название вложения',
        help_text='Название вложения'
    )
    content = models.BinaryField(
        verbose_name='Содержимое вложения',
        help_text='Содержимое вложения'
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        verbose_name='Сообщение',
        help_text='Сообщение, к которому относится вложение'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Вложение'
        verbose_name_plural = 'Вложения'
