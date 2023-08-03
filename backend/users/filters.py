"""Фильтры приложения users."""

from django.db.models import ExpressionWrapper, F, IntegerField
from django.db.models.functions import ExtractDay
from django.utils import timezone

import django_filters as df

from core.constants import LANGUAGE_SKILL_LEVELS
from users.models import User


class CustomFilterList(df.Filter):
    """Фильтрация по списку значений."""

    def filter(self, qs, value):
        if value not in (None, ''):
            values = [v for v in value.split(',')]
            return qs.filter(**{'%s__%s' %
                                (self.field_name, self.lookup_expr): values})
        return qs


class AgeFilter(df.Filter):
    """Фильтрация по возрасту."""

    def filter(self, qs, value):
        if value not in (None, ''):
            qs = qs.annotate(
                age=ExpressionWrapper(
                    ExtractDay(timezone.now().date() - F('birth_date'))
                    / 365.25,
                    output_field=IntegerField()
                )
            )
            start, end = value.split(',')
            return qs.filter(**{'%s__%s' %
                                ('age', 'range'): (start, end)})
        return qs


class UserFilter(df.FilterSet):
    """Фильтр пользователей."""

    age = AgeFilter()
    country = CustomFilterList(
        field_name='country__code', lookup_expr='in')
    native_languages = CustomFilterList(
        field_name='native_languages__isocode', lookup_expr='in')
    foreign_languages = CustomFilterList(
        field_name='foreign_languages__isocode', lookup_expr='in')
    skill_level = df.ChoiceFilter(
        choices=LANGUAGE_SKILL_LEVELS,
        field_name='userforeignlanguage__skill_level'
    )

    class Meta:
        model = User
        fields = (
            'age',
            'country',
            'gender',
            'native_languages',
            'foreign_languages',
            'skill_level',
            'is_online',
        )
