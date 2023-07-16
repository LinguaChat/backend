"""Файл административных настроек для приложения users."""

import datetime as dt

from django.contrib import admin

from .models import City, Language, User


class NativeLanguageInlineAdmin(admin.TabularInline):
    model = User.native_languages.through


class ForeignLanguageInlineAdmin(admin.TabularInline):
    model = User.foreign_languages.through


@admin.register(User)
class AdvUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        '_age',
        'country',
        'city',
        '_native_languages',
        '_foreign_languages',
        'date_joined',
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'country',
        # 'native_language__name',
        'city__name',
    )
    fields = (
        ('username', 'email', 'slug'),
        ('avatar'),
        ('first_name'),
        ('gender', 'gender_is_hidden'),
        ('phone_number'),
        ('country'),
        ('city'),
        ('birth_date', 'age_is_hidden'),
        ('about'),
        ('topics_for_discussion'),
        ('is_staff', 'is_superuser'),
        ('date_joined'),
    )
    inlines = (NativeLanguageInlineAdmin, ForeignLanguageInlineAdmin)

    def _age(self, obj):
        """Возраст пользователя."""
        if obj.birth_date:
            age_days = (dt.datetime.now().date() - obj.birth_date).days
            return int(age_days / 365)
        return None

    _age.short_description = 'Возраст'

    def _native_languages(self, obj):
        """Родной язык пользователя."""
        return ", ".join(
            [str(language) for language in obj.native_languages.all()]
        )

    _native_languages.short_description = 'Родной язык'

    def _foreign_languages(self, obj):
        """Изучаемые языки пользователя."""
        return ", ".join(
            [str(language) for language in obj.foreign_languages.all()]
        )

    _foreign_languages.short_description = 'Изучаемые языки'


admin.site.register(City)
admin.site.register(Language)
