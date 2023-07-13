import base64

from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            fmt, image_data = data.split(';base64,')
            extension = fmt.split('/')[-1]
            data = ContentFile(base64.b64decode(image_data), name='temp.' + extension)

        return super().to_internal_value(data)
