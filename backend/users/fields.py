"""Кастомные поля сериализатора приложения users."""

import base64

from django.core.files.base import ContentFile

from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Поле изображения сериализатора."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            fmt, image_data = data.split(';base64,')
            extension = fmt.split('/')[-1]
            data = ContentFile(base64.b64decode(image_data),
                               name='temp.' + extension)

        return super().to_internal_value(data)


class CreatableSlugRelatedField(serializers.SlugRelatedField):
    def to_internal_value(self, data):
        try:
            obj, created = self.get_queryset().get_or_create(
                **{self.slug_field: data}
            )
            return obj
        except (TypeError, ValueError):
            self.fail('invalid')
