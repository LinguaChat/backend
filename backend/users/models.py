"""Модели приложения users."""

from django.contrib.auth.models import AbstractUser, UserManager
from django.core.cache import cache
from django.db import models
from django.db.models import Q
from django.db.models.functions import Length
from django.template.defaultfilters import slugify
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.constants import (EMAIL_MAX_LENGTH, FIRST_NAME_MAX_LENGTH, GENDERS,
                            LANGUAGE_SKILL_LEVELS, USERNAME_MAX_LENGTH)
from core.models import AbstractNameModel, DateCreatedModel, DateEditedModel

from .validators import (custom_username_validator, validate_email,
                         validate_first_name)

models.CharField.register_lookup(Length)


class Country(AbstractNameModel):
    """Модель страны."""

    code = models.CharField(
        'Код',
        max_length=32,
        null=True,
        unique=True,
        help_text='Код страны',
    )
    flag_icon = models.ImageField(
        'Флаг',
        help_text='Флаг страны',
        upload_to='icons/countries/'
    )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ['name']
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'


class CustomUserManager(UserManager):
    """Кастомный менеджер пользователей."""

    def get_by_natural_key(self, username_or_email):
        return self.get(
            Q(**{self.model.USERNAME_FIELD: username_or_email}) |
            Q(**{self.model.EMAIL_FIELD: username_or_email})
        )


class User(AbstractUser, DateEditedModel):
    """Кастомная модель пользователя."""

    # исключаем из таблицы стобец "last_name"
    last_name = None
    ROLE_CHOICES = (
        ('user', 'User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    )
    first_name = models.CharField(
        'Имя',
        max_length=FIRST_NAME_MAX_LENGTH,
        blank=True,
        validators=[validate_first_name],
        help_text='Имя пользователя',
    )
    username = models.CharField(
        'Логин',
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        validators=[custom_username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        'Электронная почта',
        unique=True,
        help_text='Адрес email',
        max_length=EMAIL_MAX_LENGTH,
        validators=[validate_email],
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    slug = models.SlugField(
        'Слаг',
        max_length=200,
        help_text='Слаг',
        null=True,
    )
    languages = models.ManyToManyField(
        'Language',
        through='UserLanguage',
        related_name='users',
        verbose_name='Языки пользователя',
        help_text='Языки, которыми владеет пользователь',
    )
    birth_date = models.DateField(
        'Дата рождения',
        null=True,
        help_text='Дата рождения пользователя',
    )
    about = models.TextField(
        'О себе',
        max_length=256,
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
    interests = models.ManyToManyField(
        'Interest',
        related_name='users',
        verbose_name='Интересы пользователя',
        blank=True
    )
    goals = models.ManyToManyField(
        'Goal',
        related_name='users',
        verbose_name='Цели пользователя',
        blank=True
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
        upload_to='icons/users/',
        null=True,
        blank=True,
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
    last_activity = models.DateTimeField(
        'Последняя активность',
        default=timezone.now,
        blank=True,
        null=True,
        help_text='Последнее время активности пользователя',
    )
    is_online = models.BooleanField(
        default=False,
        help_text='Статус пользователя: онлайн или оффлайн',
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='user',
        help_text='Роль пользователя',
    )

    objects = CustomUserManager()

    def is_user_online(self):
        last_seen = cache.get(f'last-seen-{self.id}')
        if last_seen is not None and (
            timezone.now() < last_seen + timezone.timedelta(seconds=300)
        ):
            return True
        return False

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
            ),
            models.CheckConstraint(
                check=Q(username__length__lte=USERNAME_MAX_LENGTH),
                name="username length lte max username length"
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.username)

        if self.id or self._state.adding:
            self.last_activity = timezone.now()

            last_seen = cache.get(f'last-seen-{self.id}')
            if last_seen is not None and (
                timezone.now() < last_seen + timezone.timedelta(seconds=300)
            ):
                self.is_online = True
            else:
                self.is_online = False

        super().save(*args, **kwargs)


class Interest(models.Model):
    """Модель интересов пользователей."""

    name = models.CharField(
        'Название',
        max_length=64,
        unique=True
    )

    @property
    def sorting(self):
        return self.users.count()

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Интерес'
        verbose_name_plural = 'Интересы'
        ordering = ('name',)


class Goal(models.Model):
    """Модель целей пользователей."""

    name = models.CharField(
        'Название',
        max_length=64,
        unique=True
    )
    icon = models.ImageField(
        'Иконка',
        upload_to='icons/goals/'
    )
    sorting = models.PositiveIntegerField(
        blank=False,
        null=False,
        default=0,
        verbose_name='Порядок сортировки',
        help_text='Увеличьте, чтобы поднять в выборке'
    )

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Цель'
        verbose_name_plural = 'Цели'
        ordering = ('-sorting', 'name')


class Language(models.Model):
    """
    Модель языка.
    Объекты должны быть сгенерированы из django.conf.locale.LANG_INFO
    """

    name = models.CharField(
        max_length=256,
        null=False,
        blank=False,
        verbose_name='Название языка'
    )
    name_local = models.CharField(
        max_length=256,
        null=False,
        blank=True,
        default='',
        verbose_name='Название языка (на этом языке)'
    )
    isocode = models.CharField(
        max_length=2,
        null=False,
        blank=False,
        unique=True,
        verbose_name='ISO 639-1 Код языка',
        help_text='2-символьный код языка без страны'
    )
    sorting = models.PositiveIntegerField(
        blank=False,
        null=False,
        default=0,
        verbose_name='Порядок сортировки',
        help_text='Увеличьте, чтобы поднять в выборке'
    )

    def __str__(self):
        return '%s (%s)' % (self.name, self.name_local)

    class Meta:
        verbose_name = 'Язык'
        verbose_name_plural = 'Языки'
        ordering = ('-sorting', 'name', 'isocode', )


class UserLanguage(models.Model):
    """Модель языков пользователей."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='languages_skill',
        verbose_name='Пользователь',
        help_text='Пользователь'
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.CASCADE,
        related_name='users_skill',
        verbose_name='Язык',
        help_text='Язык'
    )
    skill_level = models.CharField(
        'Уровень владения языком',
        max_length=30,
        choices=LANGUAGE_SKILL_LEVELS,
        help_text='Укажите уровень вашего владения языком.'
    )

    def __str__(self):
        return (
            f'{self.user} знает {self.language} на уровне {self.skill_level}'
        )

    class Meta:
        verbose_name = 'Языки пользователя'
        verbose_name_plural = 'Языки пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'language'],
                name='unique_user_language'
            )
        ]


class BlacklistEntry(DateCreatedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blacklist_entries_created',
        verbose_name='Пользователь, который заблокировал',
        help_text='Пользователь, который добавил другого '
        'пользователя в черный список',
    )
    blocked_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blacklist_entries_received',
        verbose_name='Заблокированный пользователь',
        help_text='Пользователь, который был добавлен в черный список',
    )

    class Meta:
        unique_together = ('user', 'blocked_user')
        verbose_name = 'Запись в черном списке'
        verbose_name_plural = 'Записи в черном списке'

    def __str__(self):
        return f'{self.user} заблокировал {self.blocked_user}'


class Report(DateCreatedModel, DateEditedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_reports',
        verbose_name='Пользователь, отправивший жалобу',
        help_text='Пользователь, который отправил данную жалобу.',
    )
    reported_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_reports',
        verbose_name='Пользователь, на которого подана жалоба',
        help_text='Пользователь, на которого подана данная жалоба.',
    )
    reason = models.CharField(
        max_length=100,
        verbose_name='Причина жалобы',
        help_text='Укажите причину данной жалобы.',
    )
    description = models.TextField(
        verbose_name='Описание',
        max_length=1000,
        help_text='Подробное описание проблемы или причины жалобы.',
    )

    def __str__(self):
        return f"Жалоба от {self.user} на {self.reported_user}"

    class Meta:
        verbose_name = 'Жалоба на пользователя'
        verbose_name_plural = 'Жалобы на пользователей'
