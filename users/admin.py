"""Файл административных настроек для приложения users."""

from django.contrib import admin

from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админ-панель модели пользователя"""

    prepopulated_fields = {'slug': ('username',)}
