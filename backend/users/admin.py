"""Административные настройки приложения users."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    """Админ-панель модели пользователя"""

    list_display = (
        'username',
        'email',
        'first_name',
        'is_active',
        'is_staff',
        'date_joined'
    )
    list_filter = (
        'is_active',
        'is_staff',
        'date_joined'
    )
    search_fields = (
        'username',
        'email',
        'first_name'
    )
    ordering = ('-date_joined',)
    prepopulated_fields = {'slug': ('username',)}
    fieldsets = (
        (None, {
            'fields': (
                'username', 'password'
            )
        }),
        ('Personal info', {
            'fields': (
                'email',
                'first_name',
                'slug',
                'country',
                'birth_date',
                'gender',
                'phone_number',
                'city',
                'avatar',
                'about',
                'topics_for_discussion',
                'age_is_hidden',
                'gender_is_hidden'
            )
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        ('Important dates', {
            'fields': (
                'last_login',
                'date_joined'
            )
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2'
            ),
        }),
    )
