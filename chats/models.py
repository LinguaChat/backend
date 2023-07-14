"""Модели для приложения chats."""

from django.contrib.auth import get_user_model
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
