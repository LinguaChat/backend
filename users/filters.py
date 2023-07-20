import django_filters as df

from users.models import User


class CustomFilterList(df.Filter):
    """Класс для фильтрации по изучаемым языкам."""

    def filter(self, qs, value):
        if value not in (None, ''):
            values = [v for v in value.split(',')]
            return qs.filter(**{'%s__%s' %
                                (self.field_name, self.lookup_expr): values})
        return qs


class UserAgeFilter(df.FilterSet):
    """Основной фильтр по полям."""

    age = df.NumberFilter(field_name='age')
    foreign_languages = CustomFilterList(
        field_name='foreign_languages__name', lookup_expr='in')

    class Meta:
        model = User
        fields = (
            'age',
            'country',
            'gender',
            'foreign_languages',
        )
