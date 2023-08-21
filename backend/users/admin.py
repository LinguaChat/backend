"""Административные настройки приложения users."""

import datetime as dt

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (BlacklistEntry, Country, Goal, Interest, Language, Report,
                     User)


class UserLanguageInlineAdmin(admin.TabularInline):
    model = User.languages.through


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Админ-панель модели пользователя"""

    readonly_fields = (
        '_age',
        '_languages',
    )
    list_display = (
        'username',
        'email',
        'first_name',
        'role',
        'is_active',
        'is_staff',
        'date_joined',
    )
    list_filter = (
        'is_active',
        'is_staff',
        'role',
        'date_joined',
    )
    search_fields = (
        'username',
        'email',
        'role',
        'first_name',
        'country__name',
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
                '_languages',
                'birth_date',
                '_age',
                'gender',
                'avatar',
                'about',
                'interests',
                'age_is_hidden',
                'gender_is_hidden',
                'role',
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
    inlines = (UserLanguageInlineAdmin,)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'password1',
                'password2',
                'slug',
            ),
        }),
    )

    def _age(self, obj):
        """Возраст пользователя."""
        if obj.birth_date:
            age_days = (dt.datetime.now().date() - obj.birth_date).days
            return int(age_days / 365)
        return None

    _age.short_description = 'Возраст'

    def _languages(self, obj):
        """Язык пользователя."""
        return ", ".join(
            [str(language) for language in obj.languages.all()]
        )

    _languages.short_description = 'Язык, которым владеет пользователь'

    # def _foreign_languages(self, obj):
    #     """Изучаемые языки пользователя."""
    #     return ", ".join(
    #         [str(language) for language in obj.foreign_languages.all()]
    #     )

    # _foreign_languages.short_description = 'Изучаемые языки'


admin.site.register(Language)
admin.site.register(Country)
admin.site.register(BlacklistEntry)
admin.site.register(Report)
admin.site.register(Interest)
admin.site.register(Goal)
