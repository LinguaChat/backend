"""Административные настройки приложения users."""

import datetime as dt

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (BlacklistEntry, Country, Goal, Interest, Language, Report,
                     Review, User)


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


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_author_username',
                    'get_recipient_username', 'get_text', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('author__username', 'recipient__username', 'text')

    def get_author_username(self, obj):
        return obj.author.username if obj.author else None

    get_author_username.short_description = 'Автор'

    def get_recipient_username(self, obj):
        return obj.recipient.username if obj.recipient else None

    get_recipient_username.short_description = 'Получатель'

    def get_text(self, obj):
        return obj.text

    get_text.short_description = 'Текст'

    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, "Выбранные отзывы одобрены")

    approve_reviews.short_description = "Одобрить выбранные отзывы"

    def reject_reviews(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, "Выбранные отзывы отклонены")

    reject_reviews.short_description = "Отклонить выбранные отзывы"


admin.site.register(Language)
admin.site.register(Country)
admin.site.register(BlacklistEntry)
admin.site.register(Report)
admin.site.register(Interest)
admin.site.register(Goal)
