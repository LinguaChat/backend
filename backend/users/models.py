"""Модели для приложения users."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template.defaultfilters import slugify

from core.constants import GENDERS, LANGUAGE_SKILL_LEVEL
from core.models import AbstractNameModel, DateEditedModel


class User(AbstractUser, DateEditedModel):
    """Кастомная модель пользователя."""

    # исключаем из таблицы стобец "last_name"
    last_name = None

    email = models.EmailField(
        'Электронная почта',
        unique=True,
        help_text='Адрес email',
    )
    slug = models.SlugField(
        'Слаг',
        max_length=150,
        help_text='Слаг',
    )
    country = models.CharField(
        'Страна',
        max_length=50,
        null=True,
        help_text='Страна проживания пользователя',
    )
    native_languages = models.ManyToManyField(
        'Language',
        through='UserNativeLanguage',
        related_name='users_for_whom_native',
        verbose_name='Родной язык',
        help_text='Родной язык пользователя',

    )
    foreign_languages = models.ManyToManyField(
        'Language',
        through='UserForeignLanguage',
        related_name='users_who_learn',
        verbose_name='Изучаемые языки',
        help_text='Языки, которые изучает пользователь'

    )
    birth_date = models.DateField(
        'Дата рождения',
        null=True,
        help_text='Дата рождения пользователя',
    )
    about = models.TextField(
        'О себе',
        max_length=100,
        null=True,
        help_text='О себе',
    )
    gender = models.CharField(
        'Пол',
        max_length=10,
        choices=GENDERS,
        null=True,
        help_text='Пол пользователя',
    )
    topics_for_discussion = models.TextField(
        'Темы для разговора',
        max_length=100,
        null=True,
        help_text='Темы для разговора',
    )
    city = models.ForeignKey(
        'City',
        max_length=255,
        related_name='users_in_this_city',
        on_delete=models.SET_NULL,
        verbose_name='Город проживания',
        null=True,
        help_text='Город проживания пользователя',
    )
    avatar = models.ImageField(
        'Изображение',
        upload_to='user_photos/',
        null=True,
        help_text='Аватар пользователя',
    )
    age_is_hidden = models.BooleanField(
        default=False,
        help_text='Поле для скрытия/отображения возраста пользователя',
    )
    gender_is_hidden = models.BooleanField(
        default=False,
        help_text='Поле для скрытия/отображения пола пользователя',
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
    """Абстрактная модель для создания
     промежуточных моделей пользователь-родной язык
     и пользователь-иностранный язык."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Пользователь',
        help_text='Пользователь',
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Язык',
        help_text='Язык',

    )

    class Meta:
        abstract = True


class UserNativeLanguage(UserLanguage):
    """Промежуточная таблица для связи
    пользователь-родной язык."""

    class Meta:
        verbose_name = 'Пользователь -> родной язык'
        verbose_name_plural = 'Пользователи -> родные языки'

    def __str__(self):
        return f'{self.language} является родным для {self.user}'


class UserForeignLanguage(UserLanguage):

    """Промежуточная таблица для связи
    пользователь-иностранный язык."""

    skill_level = models.CharField(
        'Уровень владения языком',
        max_length=30,
        choices=LANGUAGE_SKILL_LEVEL,
        help_text='Укажите уровень вашего владения языком.',
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
