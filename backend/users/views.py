"""View-функции приложения users."""

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserViewSet
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.filters import UserFilter
from users.models import BlacklistEntry, Country, Language, Report, User
from users.serializers import (
    CountrySerializer, LanguageSerializer, ReportSerializer
)


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
        user.age_is_hidden = True if not user.age_is_hidden else False
        user.save()
        return Response(
            {"age_is_hidden": user.age_is_hidden},
            status=status.HTTP_200_OK
        )

    @action(
        methods=('PATCH',),
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=None
    )
    def hide_show_gender(self, request):
        """Метод для отображения/скрытия пола."""
        user = request.user
        user.gender_is_hidden = True if not user.gender_is_hidden else False
        user.save()
        return Response(
            {"gender_is_hidden": user.gender_is_hidden},
            status=status.HTTP_200_OK
        )

    @action(
        methods=('POST',),
        detail=True,
        permission_classes=(IsAuthenticated,),
        serializer_class=None
    )
    def block_user(self, request, slug=None):
        """Метод для блокировки пользователя."""
        user = self.get_object()
        current_user = request.user

        if user == current_user:
            return Response(
                {"detail": "Нельзя заблокировать самого себя"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if BlacklistEntry.objects.filter(
            user=current_user, blocked_user=user
        ).exists():
            return Response(
                {"detail": "Пользователь уже заблокирован"},
                status=status.HTTP_400_BAD_REQUEST
            )
        BlacklistEntry.objects.create(
            user=current_user,
            blocked_user=user,
        )
        return Response(
            {"detail": "Пользователь успешно заблокирован"},
            status=status.HTTP_200_OK
        )

    @action(
        methods=('POST',),
        detail=True,
        permission_classes=(IsAuthenticated,),
        serializer_class=None
    )
    def report_user(self, request, slug=None):
        """Метод для отправки жалобы на пользователя."""
        user = self.get_object()
        current_user = request.user

        if user == current_user:
            return Response(
                {"detail": "Нельзя отправить жалобу самому на себя."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if Report.objects.filter(
            user=current_user, reported_user=user
        ).exists():
            return Response(
                {"detail": "Жалоба уже отправлена"},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = ReportSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['reported_user'] = user
            serializer.save(user=current_user)
            return Response(
                {"detail": "Жалоба успешно отправлена."},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


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
