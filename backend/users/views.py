"""View-функции приложения users."""

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserViewSet
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.filters import UserFilter
from users.models import Country, Language, User
from users.serializers import (CountrySerializer, LanguageSerializer,
                               UserSerializer)


@extend_schema(tags=['users'])
class UserViewSet(DjoserViewSet):
    """Вьюсет модели пользователя."""

    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = UserFilter
    ordering_fields = ['date_joined']
    ordering = ['?']
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        """Исключает из выборки админов."""
        return User.objects.filter(is_staff=False)

    @action(
        methods=('PATCH',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=None
    )
    def hide_show_age(self, request):
        """Метод для отображения/скрытия возраста."""
        user = request.user
        user.age_is_hidden = 1 if not user.age_is_hidden else 0
        user.save()
        serializer = UserSerializer(
            user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=('PATCH',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=None
    )
    def hide_show_gender(self, request):
        """Метод для отображения/скрытия пола."""
        user = request.user
        user.gender_is_hidden = 1 if not user.gender_is_hidden else 0
        user.save()
        serializer = UserSerializer(
            user, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['languages'])
class LanguageViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет модели языка."""

    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    lookup_field = 'isocode'
    pagination_class = None
    permission_classes = [
        AllowAny,
    ]
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = (
        'name', 'name_local', 'isocode'
    )


@extend_schema(tags=['countries'])
class CountryViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет модели страны."""

    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    lookup_field = 'code'
    pagination_class = None
    permission_classes = [
        AllowAny,
    ]
    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = (
        'name',
    )
