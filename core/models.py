"""Абстрактные модели проекта."""

from django.db import models
from django.utils import timezone


class DateCreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""

    date_created = models.DateTimeField(
        'Дата создания',
        help_text='Дата создания',
        editable=False,
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        abstract = True


class DateEditedModel(models.Model):
    """Абстрактная модель. Добавляет дату редактирования."""

    date_edited = models.DateTimeField(
        'Дата редактирования',
        help_text='Дата изменения',
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """При сохранении обновлять временную метку."""
        self.date_edited = timezone.now()
        return super().save(*args, **kwargs)


class AbstractNameModel(models.Model):
    """Абстрактная модель. Добавляет поле имени."""

    name = models.CharField(
        'Название',
        help_text='Наименование',
        max_length=255,
    )

    class Meta:
        abstract = True
