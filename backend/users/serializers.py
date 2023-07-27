"""Сериализаторы приложения users."""

import datetime as dt

from djoser.serializers import UserSerializer as DjoserSerializer
from rest_framework import serializers

from core.constants import MAX_FOREIGN_LANGUAGES, MAX_NATIVE_LANGUAGES
from users.fields import Base64ImageField
from users.models import (Country, Language, User, UserForeignLanguage,
                          UserNativeLanguage)


class LanguageSerializer(serializers.ModelSerializer):
    """Сериализатор модели языка."""

    class Meta:
        model = Language
        fields = (
            'name',
            'name_local',
            'isocode',
            'sorting',
        )


class UserLanguageBaseSerializer(serializers.ModelSerializer):
    """Общий сериализатор промежуточных моделей Пользователь-Язык."""

    id = serializers.ReadOnlyField(source='language.id')
    language = serializers.ReadOnlyField(source='language.name')


class UserNativeLanguageSerializer(UserLanguageBaseSerializer):
    """Сериализатор промежутоной модели Пользователь-родной язык."""

    class Meta:
        model = UserNativeLanguage
        fields = (
            'id',
            'language',
        )
        read_only_fields = (
            'language',
        )


class UserForeignLanguageSerializer(UserLanguageBaseSerializer):
    """Сериализатор промежутоной модели Пользователь-иностранный язык."""

    class Meta:
        model = UserForeignLanguage
        fields = (
            'id',
            'language',
            'skill_level',
        )
        read_only_fields = (
            'language',
        )


class CountrySerializer(serializers.ModelSerializer):
    """Сериализатор модели страны."""

    class Meta:
        model = Country
        fields = (
            'code',
            'name',
            'flag_icon',
        )


class UserSerializer(DjoserSerializer):
    """Сериализатор модели пользователя."""

    age = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)
    country = CountrySerializer(read_only=True)
    native_languages = UserNativeLanguageSerializer(
        source='usernativelanguage',
        many=True,
        read_only=True
    )
    foreign_languages = UserForeignLanguageSerializer(
        source='userforeignlanguage',
        many=True,
        read_only=True
    )

    default_error_messages = {
        'out_of_range': (
            'Кол-во {objects} не должно превышать {max_amount}.'
        )
    }

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'password',
            'first_name',
            'avatar',
            'age',
            'slug',
            'country',
            'birth_date',
            'native_languages',
            'foreign_languages',
            'gender',
            'topics_for_discussion',
            'about',
        )
        extra_kwargs = {
            'email': {'write_only': True},
            'username': {'write_only': True},
            'password': {'write_only': True},
            'birth_date': {'write_only': True},
        }

    def get_age(self, obj):
        """Вычисление возраста пользователя."""
        if obj.birth_date:
            age_days = (dt.datetime.now().date() - obj.birth_date).days
            return int(age_days / 365)
        return None

    def validate(self, attrs):
        native_languages = attrs.get('native_languages')

        if (
            native_languages and
            len(native_languages) > MAX_NATIVE_LANGUAGES
        ):
            self.fail(
                'out_of_range',
                objects='родных языков',
                max_amount=MAX_NATIVE_LANGUAGES
            )

        foreign_languages = attrs.get('foreign_languages')

        if (
            foreign_languages and
            len(foreign_languages) > MAX_FOREIGN_LANGUAGES
        ):
            self.fail(
                'out_of_range',
                objects='изучаемых языков',
                max_amount=MAX_FOREIGN_LANGUAGES
            )

        return super().validate(attrs)

    def create_native_languages(self, user, native_languages):
        """Создание объектов в промежуточной таблице."""
        for language in native_languages:
            UserNativeLanguage.objects.create(
                user=user,
                language_id=language.get('id'),
            )

    def create_foreign_languages(self, user, foreign_languages):
        """Создание объектов в промежуточной таблице."""
        for language in foreign_languages:
            UserForeignLanguage.objects.create(
                user=user,
                language_id=language.get('id'),
                skill_level=language.get('skill_level'),
            )

    def to_internal_value(self, data):
        """Кастомный метод to_internal_value, учитывающий
        наличие/отсутствие запроса на запись данных в through-таблицу."""
        fields = {
            'foreign_languages': None,
            'native_languages': None
        }
        for key in fields.keys():
            if key in data:
                fields[key] = data.pop(key)

        result = super().to_internal_value(data)

        for key, value in fields.items():
            if value:
                result[key] = value

        return result

    def update(self, instance, validated_data):
        """Кастомные метод update, учитывающий
        наличие/отсутствие запроса на обновление through-таблицы."""
        if 'foreign_languages' in validated_data:
            self.create_foreign_languages(
                user=instance,
                foreign_languages=validated_data.pop('foreign_languages'),
            )
        return super().update(instance, validated_data)
