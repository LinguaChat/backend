"""View-функции для приложения users."""
import datetime as dt

from django.db.models import ExpressionWrapper, F, IntegerField
from django.db.models.functions import ExtractYear
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserViewSet
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.filters import UserAgeFilter
from users.models import User


@extend_schema(tags=['Users'])
class UserViewSet(DjoserViewSet):
    """Вьюсет для модели пользователя."""

    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserAgeFilter

    def get_queryset(self):
        """Переопределенный метод - аннотирует
        queryset поле 'age' - высчитывает возраст пользователя."""
        # вычисляем возраст на уровне БД
        queryset = User.objects.all().annotate(
            birth_year=ExtractYear('birth_date')).annotate(
                    age=ExpressionWrapper(
                        dt.datetime.now().year - F('birth_year'),
                        output_field=IntegerField())
            )

        return queryset

    @action(
        methods=('PATCH',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        # сериализатор не нужен, т.к. нет отправки/получения данных
        serializer_class=None
    )
    def hide_show_age(self, request):
        """Метод для отображения/скрытия возраста."""
        user = request.user
        user.age_is_hidden = 1 if not user.age_is_hidden else 0
        request.user.save()
        return Response(status=status.HTTP_200_OK)

    @action(
        methods=('PATCH',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        # сериализатор не нужен, т.к. нет отправки/получения данных
        serializer_class=None
    )
    def hide_show_gender(self, request):
        """Метод для отображения/скрытия пола."""
        user = request.user
        user.gender_is_hidden = 1 if not user.gender_is_hidden else 0
        request.user.save()
        return Response(status=status.HTTP_200_OK)
