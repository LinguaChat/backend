"""Кастомные валидаторы приложения users."""

import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from core.constants import (FIRST_NAME_MAX_LENGTH, FIRST_NAME_MIN_LENGTH,
                            PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH,
                            USERNAME_MIN_LENGTH)


class CustomPasswordValidator:
    """
    Пользовательский валидатор паролей.
    """

    def __init__(
        self, min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = re.compile(
            r'^(?![0-9]+$)'
            r'(?![a-zA-Z]+$)'
            r'(?![!@#%^$*+&_-]+$)'
            r'(?!.*[.])'
            r'[a-zA-Z0-9!@#%^$*+&_-]+$'
        )

    def validate(self, password, user=None):
        password_length_error = (
            f'Длина пароля должна быть от {self.min_length} '
            f'до {self.max_length} символов.'
        )
        password_invalid_error = 'Пароль не соответствует требованиям.'

        if (
            len(password) < self.min_length
            or len(password) > self.max_length
        ):
            raise ValidationError(
                {'password': password_length_error},
                code='password_length'
            )
        if ' ' in password:
            raise ValidationError(
                {'password': 'Пароль не должен содержать пробелов.'},
                code='password_invalid'
            )
        if not self.pattern.match(password):
            raise ValidationError(
                {'password': password_invalid_error},
                code='password_invalid'
            )

    def get_help_text(self):
        return _('Your password can’t contain spaces')


def custom_username_validator(value):
    """
    Пользовательский валидатор логинов.
    """
    pattern = re.compile(r'^[a-zA-Z0-9]+([._-][a-zA-Z0-9]+)*$')
    if ' ' in value:
        raise ValidationError(
            _('Логин пользователя не должен содержать пробелов.')
        )

    if len(value) < USERNAME_MIN_LENGTH:
        raise ValidationError(
            _('Длина логина пользователя должна быть от 3 до 12 символов.')
        )

    if not pattern.match(value):
        raise ValidationError(
            _('Недопустимый логин пользователя.')
        )

    if value.isdigit():
        raise ValidationError(
            _('Логин не может состоять только из цифр.')
        )


def validate_email(email):
    """
    Пользовательский валидатор почты.
    """
    if ' ' in email:
        raise ValidationError(
            _('Адрес электронной почты не должен содержать пробелов.'))

    pattern = re.compile(
        r'^[a-zA-Z][a-zA-Z0-9_]*'
        r'([._-][a-zA-Z0-9]+)*'
        r'[a-zA-Z0-9]+'
        r'@[a-zA-Z0-9.-]+'
        r'\.[a-zA-Z]{2,4}$'
    )
    if not pattern.match(email):
        raise ValidationError(
            _('Некорректный адрес электронной почты.')
        )


def validate_first_name(value):
    """
    Пользовательский валидатор имени.
    """
    pattern = re.compile(
        r'^[A-Za-zА-ЯЁа-яё]+'
        r'(?:[- ][A-Za-zА-ЯЁа-яё]+)?'
        r'(?:[- ][A-Za-zА-ЯЁа-яё]+)?$'
    )

    if not pattern.match(value):
        raise ValidationError(
            _('Некорректное имя.'))

    if (
            len(value) < FIRST_NAME_MIN_LENGTH
            or len(value) > FIRST_NAME_MAX_LENGTH
    ):
        raise ValidationError(
            _('Длина имени должна быть от 2 до 12 символов.'))
