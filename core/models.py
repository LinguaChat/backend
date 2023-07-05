from django.db import models
from django.utils import timezone


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""
    created = models.DateTimeField(
        'Дата создания',
        editable=False,
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True


class ModifiedModel(models.Model):
    """Абстрактная модель. Добавляет дату редактирования."""
    modified = models.DateTimeField(
        'Дата редактирования',
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        ''' При сохранении обновлять временную метку '''
        self.modified = timezone.now()
        return super(ModifiedModel, self).save(*args, **kwargs)
