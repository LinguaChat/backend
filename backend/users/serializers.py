"""Сериализаторы приложения users."""

from django.core.cache import cache
from django.utils import timezone

from djoser.serializers import UserCreateSerializer as DjoserCreateSerializer
from djoser.serializers import UserSerializer as DjoserSerializer
from rest_framework import serializers

from core.constants import (MAX_AGE, MAX_FOREIGN_LANGUAGES,
                            MAX_NATIVE_LANGUAGES, MIN_AGE)
from users.fields import Base64ImageField, CreatableSlugRelatedField
from users.models import (BlacklistEntry, Country, Goal, Interest, Language,
                          Report, User, UserLanguage)

from .validators import ReportDescriptionValidator


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


class UserLanguageSerializer(serializers.ModelSerializer):
    """Сериализатор языков пользователей."""

    isocode = serializers.CharField(source='language.isocode')
    language = serializers.ReadOnlyField(source='language.name')

    class Meta:
        model = UserLanguage
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


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ('name', 'icon')
        read_only_fields = fields


class UserReprSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра пользователя."""

    age = serializers.SerializerMethodField()
    avatar = Base64ImageField(read_only=True)
    country = CountrySerializer(read_only=True, many=False)
    goals = GoalSerializer(read_only=True, many=True)
    interests = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='name'
    )
    languages = UserLanguageSerializer(
        source='languages_skill',
        many=True,
        read_only=True
    )
    is_online = serializers.BooleanField(
        source='get_is_online',
        read_only=True
    )
    role = serializers.CharField(
        source='get_role_display',
        read_only=True
    )
    is_blocked = serializers.SerializerMethodField()

    def get_is_blocked(self, obj):
        current_user = self.context['request'].user
        return obj.blacklist_entries_received.filter(
            user=current_user
        ).exists()

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'avatar',
            'age',
            'slug',
            'country',
            'languages',
            'gender',
            'goals',
            'interests',
            'about',
            'last_activity',
            'is_online',
            'gender_is_hidden',
            'age_is_hidden',
            'role',
            'is_blocked',
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


class UserProfileSerializer(DjoserSerializer, UserReprSerializer):
    """Сериализатор для заполнения профиля пользователя."""

    avatar = Base64ImageField(
        required=False,
        allow_null=True
    )
    country = serializers.SlugRelatedField(
        many=False,
        read_only=False,
        required=False,
        slug_field='code',
        queryset=Country.objects.all()
    )
    interests = CreatableSlugRelatedField(
        many=True,
        read_only=False,
        required=False,
        slug_field='name',
        queryset=Interest.objects.all()
    )
    goals = serializers.SlugRelatedField(
        many=True,
        read_only=False,
        required=False,
        slug_field='name',
        queryset=Goal.objects.all()
    )
    languages = UserLanguageSerializer(
        source='languages_skill',
        many=True,
        read_only=False,
        required=False
    )

    default_error_messages = {
        'out_of_range': (
            'Кол-во {objects} не должно превышать {max_amount}.'
        ),
        'language_duplicate': (
            'Языки повторяются.'
        )
    }

    class Meta:
        model = User
        fields = UserReprSerializer.Meta.fields + (
            'birth_date',
        )
        read_only_fields = (
            'username',
            'age',
            'slug',
            'last_activity',
            'is_online',
            'gender_is_hidden',
            'age_is_hidden',
            'role',
        )

    def validate_birth_date(self, value):
        dif = (timezone.now().date() - value)
        age = int(dif.days / 365.25)
        if age not in range(MIN_AGE, MAX_AGE + 1):
            raise serializers.ValidationError("Некорректная дата рождения.")
        return value

    def validate_languages(self, value):
        isocodes = [data['language']['isocode'] for data in value]
        if len(isocodes) != len(set(isocodes)):
            self.fail('language_duplicate')

        skill_levels = [data['skill_level'] for data in value]
        if skill_levels.count('Native') > MAX_NATIVE_LANGUAGES:
            self.fail(
                'out_of_range',
                objects='родных языков',
                max_amount=MAX_NATIVE_LANGUAGES
            )

        not_native = list(filter('Native'.__ne__, skill_levels))
        if len(not_native) > MAX_FOREIGN_LANGUAGES:
            self.fail(
                'out_of_range',
                objects='изучаемых языков',
                max_amount=MAX_FOREIGN_LANGUAGES
            )

        return value

    def update(self, instance, validated_data):
        if 'languages_skill' in validated_data:
            languages = validated_data.pop('languages_skill')
            UserLanguage.objects.filter(user=instance).delete()
            for data in languages:
                language_isocode = data['language'].get('isocode')
                language = Language.objects.get(isocode=language_isocode)
                UserLanguage.objects.create(
                    user=instance,
                    language=language,
                    skill_level=data.get('skill_level'),
                )
        return super().update(instance, validated_data)


class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'slug',
            'username',
            'first_name',
            'avatar',
        )
        read_only_fields = fields


class BlacklistEntrySerializer(serializers.ModelSerializer):
    """Сериализатор блокировки"""
    class Meta:
        model = BlacklistEntry
        fields = '__all__'
        read_only_fields = ('user',)


class ReportSerializer(serializers.ModelSerializer):
    """Сериализатор жалоб"""
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        validators=[ReportDescriptionValidator()]
    )
    close_user_access = serializers.BooleanField(
        help_text="Закрыть пользователю доступ к моей странице",
    )

    class Meta:
        model = Report
        fields = ('reason', 'description', 'close_user_access')
        read_only_fields = ('reported_user',)


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ('name', 'sorting')
        read_only_fields = fields
