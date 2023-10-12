from django.core.exceptions import ValidationError


def validate_file_size(value):
    max_size = 20 * 1024 * 1024  # 20 MB
    if value.size > max_size:
        raise ValidationError(
            'Файл слишком большой. Максимальный размер: 20 МБ.')


def validate_file_extension(value, allowed_extensions):
    if not value.name.lower().endswith(allowed_extensions):
        raise ValidationError('Недопустимый формат файла.')


def validate_pdf_extension(value):
    validate_file_extension(value, ('.pdf',))


def validate_image_extension(value):
    validate_file_extension(value, ('.jpg', '.jpeg', '.png', '.gif'))


def validate_audio_extension(value):
    validate_file_extension(value, ('.mp3', '.m4a'))
