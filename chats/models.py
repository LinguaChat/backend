from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import models
from django.utils.text import slugify

from core.models import DateCreatedModel, DateEditedModel

User = get_user_model()


class Chat(DateCreatedModel, DateEditedModel):
    """Модель чата"""
    image = models.FileField(
        upload_to='chats/',
        verbose_name='Картинка чата',
        help_text='Загрузите картинку чата',
        blank=True,
        null=True
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Название чата',
        help_text='Придумайте название чату',
        blank=True
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг',
        max_length=100,
        blank=False
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='own_chats',
        verbose_name='Создатель',
        null=True,
        blank=True
    )
    is_private = models.BooleanField(
        default=True
    )
    password = models.CharField(
        max_length=128,
        verbose_name='Пароль чата',
        help_text='Добавьте к чату пароль',
        blank=True
    )
    allow_anonymous_access = models.BooleanField(
        default=False
    )
    members = models.ManyToManyField(
        User,
        through='ChatMembers',
        verbose_name='Участники',
        help_text='Добавьте в чат участников',
        related_name='chats',
    )

    def __str__(self) -> str:
        chat_string = f'Приватный чат' if self.is_private else f'Открытый чат'
        if self.title:
            chat_string += f' `{self.title}`'
        # chat_string += f' с пользователями {self.members}'
        return chat_string

    def save(self, *args, **kwargs):
        self.slug = self.slug or slugify(self.title)
        if self.password:
            self.password = make_password(self.password)
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date_created']
        verbose_name = 'Чат'
        verbose_name_plural = 'Чаты'


class ChatMembers(DateCreatedModel):
    """Модель участников чата"""
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
        related_name='members_info',
        verbose_name='Чат'
    )
    member = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chats_info',
        verbose_name='Участник чата'
    )
    chat_is_pinned = models.BooleanField(
        default=False
    )

    def __str__(self) -> str:
        chatmembers_string = (
            f'Пользователь {self.member} - участник чата {self.chat}'
        )
        if self.chat_is_pinned:
            chatmembers_string += f' (чат закреплён)'
        return chatmembers_string

    class Meta:
        ordering = ['-date_created']
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'
        constraints = [
            models.UniqueConstraint(
                fields=['chat', 'member'],
                name='уникальные участники'
            )
        ]
