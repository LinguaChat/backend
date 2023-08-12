import re

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from core.constants import (FIRST_NAME_MAX_LENGTH, FIRST_NAME_MIN_LENGTH,
                            PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH,
                            USERNAME_MAX_LENGTH, USERNAME_MIN_LENGTH)


def custom_username_validator(value):
    pattern = re.compile(r'^[a-zA-Zа-яА-Я0-9]+([._-][a-zA-Zа-яА-Я0-9]+)*$')

    if len(value) < USERNAME_MIN_LENGTH or len(value) > USERNAME_MAX_LENGTH:
        raise serializers.ValidationError(
            {'username':
             _('Длина логина пользователя должна быть от 3 до 12 символов.')}
        )

    if not pattern.match(value):
        raise serializers.ValidationError(
            {'username': _('Недопустимый логин пользователя.')})

    if value.isdigit():
        raise serializers.ValidationError(
            {'username':
             _('Логин не может состоять только из цифр.')})


def validate_password(password):
    pattern = re.compile(
        r'^(?![0-9]+$)'
        r'(?![a-zA-Z]+$)'
        r'(?![!@#%^$*+&_-]+$)'
        r'(?!.*[.])'
        r'[a-zA-Z0-9!@#%^$*+&_-]+$'
    )

    if (
            len(password) < PASSWORD_MIN_LENGTH
            or len(password) > PASSWORD_MAX_LENGTH
    ):
        raise serializers.ValidationError(
            {'password': _('Длина пароля должна быть от 5 до 12 символов.')})

    if not pattern.match(password):
        raise serializers.ValidationError(
            {'password': _('Пароль не соответствует требованиям.')})


def validate_email(email):
    pattern = re.compile(
        r'^[a-zA-Z0-9]+'
        r'([._-][a-zA-Z0-9]+)*'
        r'[a-zA-Z0-9]+'
        r'@[a-zA-Z0-9.-]+'
        r'\.[a-zA-Z]{2,4}$'
    )
    if not pattern.match(email):
        raise serializers.ValidationError(
            {'email': _('Некорректный адрес электронной почты.')}
        )


def validate_first_name(value):
    pattern = re.compile(
        r'^[A-Za-zА-ЯЁа-яё]+'
        r'(?:[- ][A-Za-zА-ЯЁа-яё]+)?'
        r'(?:[- ][A-Za-zА-ЯЁа-яё]+)?$'
    )

    if (
            len(value) < FIRST_NAME_MIN_LENGTH
            or len(value) > FIRST_NAME_MAX_LENGTH
    ):
        raise serializers.ValidationError(
            {'first_name': _('Длина имени должна быть от 2 до 12 символов.')})

    if not pattern.match(value):
        raise serializers.ValidationError(
            {'first_name': _('Некорректное имя.')}
        )
