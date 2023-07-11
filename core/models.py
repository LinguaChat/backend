"""Файл c абстрактными моделями для всего проекта."""

from django.db import models
from django.utils import timezone


class DateCreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""

    date_created = models.DateTimeField(
        'Дата создания',
        editable=False,
        auto_now_add=True,
        db_index=True,
        help_text='Дата создания'
    )

    class Meta:
        abstract = True


class DateEditedModel(models.Model):
    """Абстрактная модель. Добавляет дату редактирования."""

    date_edited = models.DateTimeField(
        'Дата редактирования',
        blank=True,
        null=True,
        help_text='Дата изменения'
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        ''' При сохранении обновлять временную метку '''
        self.date_edited = timezone.now()
        return super(DateEditedModel, self).save(*args, **kwargs)


class AbstractNameModel(models.Model):
    """Модель, содержащее поле 'имя' для
    уменьшения дублирования кода."""

    name = models.CharField(
        'Название',
        max_length=255,
        help_text='Наименование'
    )

    class Meta:
        abstract = True
