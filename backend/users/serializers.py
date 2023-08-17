"""Сериализаторы приложения users."""

from django.core.cache import cache
from django.utils import timezone

from djoser.serializers import UserCreateSerializer as DjoserCreateSerializer
from djoser.serializers import UserSerializer as DjoserSerializer
from rest_framework import serializers

from core.constants import (MAX_AGE, MAX_FOREIGN_LANGUAGES,
                            MAX_NATIVE_LANGUAGES, MIN_AGE)
from users.fields import Base64ImageField
from users.models import (BlacklistEntry, Country, Language, Report, User, Interest,
                          UserForeignLanguage, UserNativeLanguage)


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
        read_only_fields = fields


class UserLanguageBaseSerializer(serializers.ModelSerializer):
    """Общий сериализатор промежуточных моделей Пользователь-Язык."""

    isocode = serializers.CharField(source='language.isocode')
    language = serializers.ReadOnlyField(source='language.name')


class UserNativeLanguageSerializer(UserLanguageBaseSerializer):
    """Сериализатор промежутоной модели Пользователь-родной язык."""

    class Meta:
        model = UserNativeLanguage
        fields = (
            'isocode',
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
            'isocode',
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
        read_only_fields = fields


class UserCreateSerializer(DjoserCreateSerializer):
    """Сериализатор создания пользователя."""

    default_error_messages = {
        'too_long': (
            'Длина {objects} не должна превышать {max_amount} символов.'
        ),
    }

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'password',
        )
        extra_kwargs = {
            'email': {'write_only': True},
            'username': {'write_only': True},
        }


class UserProfileSerializer(DjoserSerializer):
    """Сериализатор для заполнения профиля пользователя."""

    avatar = Base64ImageField(required=False, allow_null=True)
    country = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        required=False,
        slug_field='code',
        queryset=Country.objects.all()
    )
    interests = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        required=False,
        slug_field='name',
        queryset=Interest.objects.all()
    )
    native_languages = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        required=False,
        slug_field='isocode',
        queryset=Language.objects.all()
    )
    foreign_languages = UserForeignLanguageSerializer(
        source='userforeignlanguage',
        many=True,
        read_only=False,
        required=False
    )

    default_error_messages = {
        'out_of_range': (
            'Кол-во {objects} не должно превышать {max_amount}.'
        ),
    }

    class Meta:
        model = User
        fields = (
            'first_name',
            'avatar',
            'country',
            'birth_date',
            'native_languages',
            'foreign_languages',
            'gender',
            'interests',
            'about',
        )

    def validate_birth_date(self, value):
        dif = (timezone.now().date() - value)
        age = int(dif.days / 365.25)
        if age not in range(MIN_AGE, MAX_AGE + 1):
            raise serializers.ValidationError("Некорректная дата рождения.")
        return value

    def validate(self, attrs):

        native_languages = attrs.get('native_languages')
        if (
            native_languages
            and len(native_languages) > MAX_NATIVE_LANGUAGES
        ):
            self.fail(
                'out_of_range',
                objects='родных языков',
                max_amount=MAX_NATIVE_LANGUAGES
            )

        foreign_languages = attrs.get('foreign_languages')
        if (
            foreign_languages
            and len(foreign_languages) > MAX_FOREIGN_LANGUAGES
        ):
            self.fail(
                'out_of_range',
                objects='изучаемых языков',
                max_amount=MAX_FOREIGN_LANGUAGES
            )

        return super().validate(attrs)

    def update(self, instance, validated_data):
        if 'userforeignlanguage' in validated_data:
            foreign_languages = validated_data.pop('userforeignlanguage')
            UserForeignLanguage.objects.filter(user=instance).delete()
            for data in foreign_languages:
                language_isocode = data['language'].get('isocode')
                language = Language.objects.get(isocode=language_isocode)
                UserForeignLanguage.objects.create(
                    user=instance,
                    language=language,
                    skill_level=data.get('skill_level'),
                )
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return UserReprSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data


class UserReprSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра пользователя."""

    age = serializers.SerializerMethodField()
    avatar = Base64ImageField(read_only=True)
    country = CountrySerializer(read_only=True, many=False)
    interests = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
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
    is_online = serializers.SerializerMethodField()
    role = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'avatar',
            'age',
            'slug',
            'country',
            'native_languages',
            'foreign_languages',
            'gender',
            'interests',
            'about',
            'last_activity',
            'is_online',
            'gender_is_hidden',
            'age_is_hidden',
            'role',
        )
        read_only_fields = fields

    def get_is_online(self, obj):
        last_seen = cache.get(f'last-seen-{obj.id}')
        return last_seen is not None and (
            timezone.now() < last_seen + timezone.timedelta(seconds=300)
        )

    def get_age(self, obj):
        """Вычисление возраста пользователя."""
        if obj.birth_date:
            age_days = (timezone.now().date() - obj.birth_date).days
            return int(age_days / 365)
        return None


class BlacklistEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlacklistEntry
        fields = '__all__'
        read_only_fields = ('user',)


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('reason', 'description')
        read_only_fields = ('reported_user',)
