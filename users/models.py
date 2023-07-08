from django.contrib.auth.models import AbstractUser

from django.db import models

from core.constants import GENDERS, LANGUAGE_SKILL_LEVEL
from core.models import AbstractNameModel, DateEditedModel


class User(AbstractUser, DateEditedModel):
    """Кастомная модель пользователя."""

    # исключаем из таблица стобец "last_name"
    last_name = None

    country = models.CharField(
        max_length=50,
        verbose_name='Страна',
        null=True
    )
    native_language = models.ForeignKey(
        'Language',
        related_name='native_users',
        on_delete=models.SET_NULL,
        max_length=255,
        verbose_name='Родной язык',
        null=True
    )
    birthdate = models.DateField(
        verbose_name='Дата рождения',
        null=True
    )
    gender = models.CharField(
        max_length=10,
        verbose_name='Пол',
        choices=GENDERS,
        null=True
    )
    phone_number = models.CharField(
        max_length=30,
        verbose_name='Номер телефона',
        null=True
    )
    city = models.ForeignKey(
        'City',
        related_name='users_in_this_city',
        on_delete=models.SET_NULL,
        max_length=255,
        verbose_name='Город проживания',
        null=True
    )
    foreign_languages = models.ManyToManyField(
        'Language',
        through='UserLanguage',
        related_name='users_who_learn',
    )
    # image = ...
    # булево поле для скрытия возраста
    age_is_hidden = models.BooleanField(default=False)
    # булево поле для скрытия пола
    gender_is_hidden = models.BooleanField(default=False)

    REQUIRED_FIELDS = [
        'email',
        'first_name',
        'native_language',
    ]

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
        max_length=30,
        choices=LANGUAGE_SKILL_LEVEL,
        verbose_name='Уровень владения'
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
