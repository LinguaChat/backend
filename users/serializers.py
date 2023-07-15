"""Сериализаторы для приложения users."""

import datetime as dt

from djoser.serializers import UserSerializer as DjoserSerializer
from rest_framework import serializers

from users.fields import Base64ImageField, CityNameField, LanguageNameField
from users.models import City, Language, User, UserLanguage


class UserLanguageSerializer(serializers.ModelSerializer):
    """Сериализатор для промежутоной модели Пользователь-Язык."""

    id = serializers.ReadOnlyField(source='language.id')
    language = serializers.ReadOnlyField(source='language.name')

    class Meta:
        model = UserLanguage
        fields = (
            'id',
            'language',
            'skill_level',
        )


class UserSerializer(DjoserSerializer,):
    """Сериализатор для модели пользователя."""

    age = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)
    native_language = LanguageNameField(queryset=Language.objects.all())
    city = CityNameField(queryset=City.objects.all(), required=False)
    foreign_languages = UserLanguageSerializer(
        source='user',
        many=True,
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'password',
            'first_name',
            'image',
            'age',
            'slug',
            'country',
            'city',
            'birth_date',
            'native_language',
            'foreign_languages',
            'gender',
            'phone_number',
        )

    def get_age(self, obj):
        """Вычисляем возраст пользователя."""
        if obj.birth_date:
            age_days = (dt.datetime.now().date() - obj.birth_date).days
            return int(age_days / 365)
        return None

    def create_foreign_languages(self, user, foreign_languages):
        """Создание объектов в промежуточной таблице."""
        for language in foreign_languages:
            UserLanguage.objects.create(
                user=user,
                language_id=language.get('id'),
                skill_level=language.get('skill_level'),
            )

    def to_internal_value(self, data):
        """Кастомный метод to_internal_value, учитывающий
        наличие/отсутствие запроса на запись данных в through-таблицу."""
        if 'foreign_languages' in data:
            foreign_languages = data.pop('foreign_languages')
            result = super().to_internal_value(data)
            result['foreign_languages'] = foreign_languages
            return result
        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        """Кастомные метод update, учитывающий
        наличие/отсутствие запроса на обновление through-таблицы."""
        if 'foreign_languages' in validated_data:
            UserLanguage.objects.filter(user=instance).delete()
            self.create_foreign_languages(
                user=instance,
                foreign_languages=validated_data.pop('foreign_languages'),
            )
        return super().update(instance, validated_data)
