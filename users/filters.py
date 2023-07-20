import django_filters as df

from users.models import User


class UserAgeFilter(df.FilterSet):
    age = df.NumberFilter(field_name='age')

    class Meta:
        model = User
        fields = (
            'age',
            'country',
            'gender',
            'foreign_languages',
        )



