from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema
from djoser.views import UserViewSet as DjoserViewSet


@extend_schema(tags=['Users'])
class UserViewSet(DjoserViewSet):
    """Вьюсет для модели пользователя."""

    @action(
        methods=('PATCH',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        # сериализатор не нужен, т.к. нет отправки/получения данных
        serializer_class=None
    )
    def hide_show_age(self, request):
        """Метод для отображения/скрытия возраста."""
        request.user.age_is_hidden = 1 if not request.user.age_is_hidden else 0
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
        request.user.gender_is_hidden = 1 if not request.user.gender_is_hidden else 0
        request.user.save()
        return Response(status=status.HTTP_200_OK)


