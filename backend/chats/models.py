"""Модели для приложения chats."""

from django.contrib.auth import get_user_model
# from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# from polymorphic.models import PolymorphicModel
from model_utils.managers import InheritanceManager

from core.models import DateCreatedModel, DateEditedModel

User = get_user_model()


class Chat(DateCreatedModel, DateEditedModel):
    """Модель чата."""

    name = models.CharField(
        'Название',
        max_length=128,
        blank=True
    )
    members = models.ManyToManyField(
        User,
        verbose_name='Участники',
        help_text='Кто может просматривать и отправлять сообщения в чате',
        related_name='chats'
    )

    objects = InheritanceManager()

    def get_members_count(self):
        return self.members.count()
    
    def __str__(self):
        return f'{self.name} ({self.get_members_count()})'

    class Meta:
        ordering = ['-date_created']
        get_latest_by = 'date_created'
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'


class PersonalChat(Chat):
    """Модель личного чата."""

    class Meta:
        ordering = ['-date_created']
        get_latest_by = 'date_created'
        verbose_name = 'Личный чат'
        verbose_name_plural = 'Личные чаты'


class GroupChat(Chat):
    """Модель группового чата."""
    # creator = ...

    class Meta:
        ordering = ['-date_created']
        get_latest_by = 'date_created'
        verbose_name = 'Групповой чат'
        verbose_name_plural = 'Групповые чаты'


class Message(DateCreatedModel, DateEditedModel):
    """Модель сообщения."""

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Отправитель сообщения',
        help_text='Отправитель сообщения',
        blank=True,
        null=True
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
    read_by = models.ManyToManyField(
        User,
        verbose_name='Прочитано пользователем',
        help_text='Кем прочитано сообщение',
        related_name='read+',
        blank=True
    )
    is_pinned = models.BooleanField(
        default=False,
        verbose_name='Сообщение закреплено',
        help_text='Сообщение закреплено'
    )

    @property
    def is_read(self):
        return self.read_by.exists()

    def __str__(self):
        return (
            f'From {self.sender} [chat: {self.chat.name}]: '
            f'{self.text} [{self.date_created}]'
        )

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


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


class ChatRequest(DateCreatedModel):
    """Модель для запросов и приглашений."""
    
    from_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="requests_from_me"
    )
    to_user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="requests_to_me"
    )
    message = models.CharField(
        max_length=512,
        verbose_name='Текст сообщения',
        help_text='Текст сообщения'
    )

    objects = InheritanceManager()

    def __str__(self):
        return f'Запрос от {self.from_user} к {self.to_user}: {self.message}'

    class Meta:
        ordering = ['-date_created']
        get_latest_by = 'date_created'
        verbose_name = 'Приглашение в чат'
        verbose_name_plural = 'Приглашения в чаты'


class PersonalChatRequest(ChatRequest):

    def __str__(self):
        return (
            f'Пользователь {self.from_user} хочет начать общение с '
            f'{self.to_user}: {self.message}'
        )

    class Meta:
        ordering = ['-date_created']
        get_latest_by = 'date_created'
        verbose_name = 'Запрос начать личный чат'
        verbose_name_plural = 'Запросы на личные чаты'


class GroupChatRequest(ChatRequest):
    # chat = ...

    def __str__(self):
        return (
            f'Приглашение в чат {self.chat} от {self.from_user}: '
            f'{self.message}'
        )

    class Meta:
        ordering = ['-date_created']
        get_latest_by = 'date_created'
        verbose_name = 'Приглашение в групповой чат'
        verbose_name_plural = 'Приглашения в групповые чаты'
