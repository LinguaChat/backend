"""Файл c моделями для приложения users."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template.defaultfilters import slugify

from core.constants import GENDERS, LANGUAGE_SKILL_LEVEL
from core.models import AbstractNameModel, DateEditedModel


class User(AbstractUser, DateEditedModel):
    """Кастомная модель пользователя."""

    # исключаем из таблицы стобец "last_name"
    last_name = None

    slug = models.SlugField(
        'Слаг',
        max_length=150,
        help_text='Слаг'
    )
    country = models.CharField(
        'Страна',
        max_length=50,
        null=True,
        help_text='Страна проживания пользователя'
    )
    native_language = models.ForeignKey(
        'Language',
        max_length=255,
        related_name='native_users',
        on_delete=models.SET_NULL,
        verbose_name='Родной язык',
        help_text='Родной язык пользователя',
        null=True
    )
    birthdate = models.DateField(
        'Дата рождения',
        null=True,
        help_text='Дата рождения пользователя',
    )
    gender = models.CharField(
        'Пол',
        max_length=10,
        choices=GENDERS,
        null=True,
        help_text='Пол пользователя',
    )
    phone_number = models.CharField(
        'Номер телефона',
        max_length=30,
        null=True,
        help_text='Номер телефона пользователя',
    )
    city = models.ForeignKey(
        'City',
        max_length=255,
        related_name='users_in_this_city',
        on_delete=models.SET_NULL,
        verbose_name='Город проживания',
        null=True,
        help_text='Город проживания пользователя'
    )
    foreign_languages = models.ManyToManyField(
        'Language',
        through='UserLanguage',
        related_name='users_who_learn',
        verbose_name='Изучаемые языки',
        help_text='Языки, которые изучает пользователь'
    )
    # image = ...
    age_is_hidden = models.BooleanField(
        default=False,
        help_text='Поле для скрытия/отображения возраста пользователя'
    )
    # булево поле для скрытия пола
    gender_is_hidden = models.BooleanField(
        default=False,
        help_text='Поле для скрытия/отображения пола пользователя'
    )

    def __str__(self):
        return f'Пользователь {self.first_name}'

    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='уникальные пользователи'
            )
        ]

    def save(self, *args, **kwargs):
        """При создании объекта устанавливать слаг."""
        if not self.id:
            self.slug = slugify(self.username)
        super().save(*args, **kwargs)


class Language(AbstractNameModel):
    """Модель изучаемого языка."""

    class Meta:
        ordering = ('name',)
        verbose_name = 'Изучаемый язык'
        verbose_name_plural = 'Изучаемые языки'

    def __str__(self):
        return self.name


class UserLanguage(models.Model):
    """Промежуточная модель пользователь-язык."""

    user = models.ForeignKey(
        User,
        related_name='user',
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    language = models.ForeignKey(
        Language,
        related_name='language',
        on_delete=models.CASCADE,
        verbose_name='Язык'
    )
    skill_level = models.CharField(
        'Уровень владения языком',
        max_length=30,
        choices=LANGUAGE_SKILL_LEVEL,
        help_text='Укажите уровень вашего владения языком.'
    )

    class Meta:
        verbose_name = 'Пользователь -> изучаемый язык'
        verbose_name_plural = 'Пользователи -> изучаемые языки'

    def __str__(self):
        return f'{self.user} изучает {self.language}'


class City(AbstractNameModel):
    """Модель города проживания пользователя."""

    class Meta:
        ordering = ('name',)
        verbose_name = 'Город проживания'
        verbose_name_plural = 'Города проживания'

    def __str__(self):
        return self.name
