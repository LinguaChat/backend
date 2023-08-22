"""View-функции приложения users."""

from django.db.models import Count, Q
from django.utils import timezone

from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserViewSet
from drf_spectacular.utils import (OpenApiExample, OpenApiParameter,
                                   extend_schema, extend_schema_view,
                                   inline_serializer)
from rest_framework import filters, mixins, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from chats.models import PersonalChatRequest
from core.permissions import (CanAccessProfileDetails,
                              IsAdminOrModeratorReadOnly)
from users.filters import UserFilter
from users.models import (BlacklistEntry, Country, Goal, Interest, Language,
                          Report, User)
from users.serializers import (CountrySerializer, GoalSerializer,
                               InterestSerializer, LanguageSerializer,
                               ReportSerializer, UserProfileSerializer,
                               UserReprSerializer)


@extend_schema(tags=['users'])
@extend_schema_view(
    list=extend_schema(
        summary='Просмотреть всех пользователей',
        request=UserProfileSerializer,
        responses={
            status.HTTP_200_OK: UserReprSerializer,
        },
        description=(
            'Просмотреть всех пользователей с применением фильтров '
            'и сортировки. Админы и модераторы из выборки исключены'
        ),
    ),
    retrieve=extend_schema(
        summary='Просмотреть профиль пользователя',
        responses={
            status.HTTP_200_OK: UserReprSerializer,
        },
        description="Просмотреть профиль пользователя с соответствующим slug",
    ),
    create=extend_schema(
        summary='Зарегистрироваться',
        description='Создать нового пользователя',
        examples=[
                OpenApiExample(
                    "Create user example",
                    description="Test example for the new user",
                    value={
                        "email": "user@example.com",
                        "username": "newuser",
                        "password": "string"
                    },
                    status_codes=[str(status.HTTP_200_OK)],
                ),
        ],
    ),
    me=extend_schema(
        parameters=[
            OpenApiParameter(
                name='Authorization',
                location=OpenApiParameter.HEADER,
                description='Bearer access token',
                required=True,
                type=str
            ),
        ]
    ),
    set_password=extend_schema(
        summary='Изменить пароль на новый',
        description='Изменить пароль на новый',
    ),
    hide_show_age=extend_schema(
        summary='Изменить видимость возраста в своем профиле',
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="AgeVisibility",
                fields={"age_is_hidden": serializers.BooleanField()}
            ),
        },
        description='Изменить видимость возраста в своем профиле',
    ),
    hide_show_gender=extend_schema(
        summary='Изменить видимость пола в своем профиле',
        responses={
            status.HTTP_200_OK: inline_serializer(
                name="GenderVisibility",
                fields={"gender_is_hidden": serializers.BooleanField()}
            ),
        },
        description='Изменить видимость пола в своем профиле',
    ),
    block_user=extend_schema(
        summary='Заблокировать пользователя',
        description='Заблокировать пользователя',
    ),
    unblock_user=extend_schema(
        summary='Разблокировать пользователя',
        description='Разблокировать пользователя',
    ),
)
class UserViewSet(DjoserViewSet):
    """Вьюсет модели пользователя."""

    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = UserFilter
    permission_classes = [CanAccessProfileDetails]
    ordering_fields = ['date_joined']
    ordering = ['?']
    lookup_field = 'slug'
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        """Исключение админов и модераторов из выборки."""
        return User.objects.filter(Q(is_staff=False) | Q(role="User"))

    @extend_schema(
        summary='Редактировать свой профиль',
        description='Редактировать свой профиль',
        methods=["patch"]
    )
    @extend_schema(
        summary='Просмотреть свой профиль',
        description='Просмотреть свой профиль',
        methods=["get"],
        responses={
            status.HTTP_200_OK: UserReprSerializer,
        },
    )
    @extend_schema(
        summary='Удалить свой аккаунт',
        description='Удалить свой аккаунт',
        methods=["delete"]
    )
    @action(
        methods=["get", "patch", "delete"],
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request, *args, **kwargs):
        """Взаимодействие со своим профилем"""
        return super().me(request, *args, **kwargs)

    @action(
        methods=["patch"],
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=None
    )
    def hide_show_age(self, request):
        """Изменение видимости возраста"""
        user = request.user
        user.age_is_hidden = True if not user.age_is_hidden else False
        user.save()
        return Response(
            {"age_is_hidden": user.age_is_hidden},
            status=status.HTTP_200_OK
        )

    @action(
        methods=["patch"],
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=None
    )
    def hide_show_gender(self, request):
        """Изменение видимости пола."""
        user = request.user
        user.gender_is_hidden = True if not user.gender_is_hidden else False
        user.save()
        return Response(
            {"gender_is_hidden": user.gender_is_hidden},
            status=status.HTTP_200_OK
        )

    @action(
        methods=["post"],
        detail=True,
        permission_classes=(IsAuthenticated,),
        serializer_class=None
    )
    def block_user(self, request, slug=None):
        """Блокировка пользователя."""
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
        methods=["post"],
        detail=True,
        permission_classes=(IsAuthenticated,),
        serializer_class=None
    )
    def unblock_user(self, request, slug=None):
        """Отмена блокировки пользователя."""
        user = self.get_object()
        current_user = request.user

        if BlacklistEntry.objects.filter(
            user=current_user, blocked_user=user
        ).exists():
            BlacklistEntry.objects.filter(
                user=current_user, blocked_user=user
            ).delete()
            return Response(
                {"detail": "Пользователь успешно разблокирован"},
                status=status.HTTP_200_OK
            )
        return Response(
            {"detail": "Пользователь не заблокирован"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        summary='Просмотреть все жалобы на пользователя',
        description=(
            'Просмотреть все жалобы на пользователя '
            '(для админов и модераторов)'
        ),
        methods=["get"]
    )
    @extend_schema(
        summary='Отправить жалобу на пользователя',
        description='Отправить жалобу на пользователя',
        methods=["post"]
    )
    @action(
        methods=["post", "get"],
        detail=True,
        permission_classes=(IsAuthenticated, IsAdminOrModeratorReadOnly),
        serializer_class=None
    )
    def report_user(self, request, slug=None):
        """Просмотр и отправка жалоб."""
        user = self.get_object()
        current_user = request.user

        if request.method == 'POST':
            existing_report = Report.objects.filter(
                user=current_user, reported_user=user).first()

            if existing_report and (
                    existing_report.date_created + timezone.timedelta(weeks=1)
                    > timezone.now()
            ):
                return Response(
                    {"detail": "Вы не можете отправлять жалобу часто."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if existing_report:
                existing_report.date_created = timezone.now()
                existing_report.reason = request.data.get(
                    'reason', existing_report.reason)
                existing_report.description = request.data.get(
                    'description', existing_report.description)
                existing_report.save()
            else:
                serializer = ReportSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save(user=current_user, reported_user=user)
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(
                {"detail": "Жалоба успешно отправлена."},
                status=status.HTTP_200_OK
            )

        reports = Report.objects.filter(reported_user=user)
        serializer = ReportSerializer(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=["post"],
        detail=True,
        permission_classes=(IsAuthenticated,),
        serializer_class=None
    )
    def start_chat(self, request, slug=None):
        """Отправка запроса на личный чат."""
        user = self.get_object()
        current_user = request.user
        message = request.data.pop('message', None)

        user_request, created = PersonalChatRequest.objects.get_or_create(
            from_user=current_user,
            to_user=user,
            message=message
        )
        if not created:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_201_CREATED)


@extend_schema(tags=['languages'])
@extend_schema_view(
    list=extend_schema(
        summary='Просмотреть все языки',
        description=(
            'Просмотреть все языки с возможностью поиска по их кодам '
            'и названиям'
        ),
    ),
    retrieve=extend_schema(
        summary='Просмотреть информацию об языке',
        description="Просмотреть информацию об языке с соответствующим кодом",
    ),
)
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


@extend_schema_view(
    list=extend_schema(
        summary='Просмотреть все страны',
        description=(
            'Просмотреть все страны с возможностью поиска по их кодам '
            'и названиям'
        ),
    ),
    retrieve=extend_schema(
        summary='Просмотреть информацию о стране',
        description="Просмотреть информацию о стране с соответствующим кодом",
    ),
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


@extend_schema(tags=['interests'])
@extend_schema_view(
    list=extend_schema(
        summary='Список интересов',
        description=(
            'Просмотреть список всех интересов пользователей'
        ),
    )
)
class InterestViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Просмотр списка интересов."""

    serializer_class = InterestSerializer
    permission_classes = [
        AllowAny,
    ]
    filter_backends = [
        filters.SearchFilter
    ]
    search_fields = (
        'name',
    )

    def get_queryset(self):
        return Interest.objects.annotate(
            users_count=Count('users')
        ).order_by('-users_count')


@extend_schema(tags=['goals'])
@extend_schema_view(
    list=extend_schema(
        summary='Список целей',
        description=(
            'Просмотреть список целей'
        ),
    )
)
class GoalViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Просмотр списка целей."""

    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [
        AllowAny,
    ]
