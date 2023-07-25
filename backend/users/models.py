"""Модели приложения users."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext as _

from core.constants import GENDERS, LANGUAGE_SKILL_LEVEL
from core.models import AbstractNameModel, DateEditedModel


class Country(AbstractNameModel):
    """Модель страны."""

    code = models.CharField(
        'Код',
        max_length=2,
        null=True,
        unique=True,
        help_text='Код страны',
    )
    flag_icon = models.ImageField(
        'Флаг',
        help_text='Флаг страны',
    )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'


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
        null=True
    )
    country = models.CharField(
        'Страна',
        max_length=50,
        blank=True,
        help_text='Страна проживания пользователя',
    )
    native_languages = models.ManyToManyField(
        'Language',
        through='UserNativeLanguage',
        related_name='native_for',
        verbose_name='Родной язык',
        help_text='Родной язык пользователя',
    )
    foreign_languages = models.ManyToManyField(
        'Language',
        through='UserForeignLanguage',
        related_name='learned_by',
        verbose_name='Изучаемые языки',
        help_text='Языки, которые изучает пользователь',
    )
    birth_date = models.DateField(
        'Дата рождения',
        null=True,
        help_text='Дата рождения пользователя',
    )
    about = models.TextField(
        'О себе',
        max_length=100,
        blank=True,
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
        blank=True,
        help_text='Темы для разговора',
    )
    country = models.ForeignKey(
        'Country',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Страна',
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
        if self.first_name:
            return f'{self.first_name} ({self.username})'
        return f'{self.username}'

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


class Language(models.Model):
    '''
    List of languages by iso code (2 letter only because country code
    is not needed.
    This should be popluated by getting data from django.conf.locale.LANG_INFO
    '''

    name = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        verbose_name=_('Language name')
    )
    name_local = models.CharField(
        max_length=256,
        null=False,
        blank=True,
        default='',
        verbose_name=_('Language name (in that language)')
    )
    isocode = models.CharField(
        max_length=2,
        null=False,
        blank=False,
        unique=True,
        verbose_name=_('ISO 639-1 Language code'),
        help_text=_('2 character language code without country')
    )
    sorting = models.PositiveIntegerField(
        blank=False,
        null=False,
        default=0,
        verbose_name=_('Sorting order'),
        help_text=_('Increase to show at top of the list')
    )

    def __str__(self):
        return '%s (%s)' % (self.name, self.name_local)

    class Meta:
        verbose_name = _('Language')
        verbose_name_plural = _('Languages')
        ordering = ('-sorting', 'name', 'isocode', )


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
