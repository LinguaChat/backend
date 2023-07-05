from django.db import models
from django.utils import timezone


class CreatedModifiedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания и редактирования."""
    created = models.DateTimeField(
        'Дата создания',
        editable=False,
        db_index=True
    )
    modified = models.DateTimeField(
        'Дата редактирования',
        blank=True,
        null=True
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        ''' При сохранении обновлять временные метки '''
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(CreatedModifiedModel, self).save(*args, **kwargs)
