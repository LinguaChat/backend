"""Конфигурация приложения users."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Приложение для описания пользователя'

    # def ready(self):
    #     # Импортируем модуль с определениями сигналов
    #     import users.signals  # noqa
