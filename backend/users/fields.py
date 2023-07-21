"""Кастомные поля сериализатора приложения users."""

import base64

from django.core.files.base import ContentFile
from rest_framework import serializers

from users.models import City, Language


class Base64ImageField(serializers.ImageField):
    """Поле изображения сериализатора."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            fmt, image_data = data.split(';base64,')
            extension = fmt.split('/')[-1]
            data = ContentFile(base64.b64decode(image_data),
                               name='temp.' + extension)

        return super().to_internal_value(data)


class CityNameField(serializers.RelatedField):
    """Кастомное поле, позволяющее делать update
    города по id и получать его строковое
    название при GET-запросе."""

    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        return City.objects.get(id=data)


class LanguageNameField(serializers.RelatedField):
    """Кастомное поле, позволяющее делать update
    языка по id и получать его строковое
    название при GET-запросе."""

    def to_representation(self, value):
        return value.name

    def to_internal_value(self, data):
        return Language.objects.get(id=data)
