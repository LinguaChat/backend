from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from core.pagination import LimitPagination

from .serializers import ChatSerializer

User = get_user_model()


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    http_method_names = ['get', 'post', 'head', 'patch', 'delete']
    permission_classes = [
        IsAuthenticated,
    ]
    pagination_class = LimitPagination
    filter_backends = [
        filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend
    ]
    filterset_fields = (
        'is_private',
    )
    search_fields = (
        'title', 'members__username', 'members__first_name'
    )
    ordering = ('-date_created',)

    def get_queryset(self):
        return self.request.user.chats.all()

    def get_permissions(self):
        if self.action == 'create':
            return (AllowAny(),)
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        """Просмотреть свои чаты"""
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Просмотреть чат"""
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """Редактировать общую информацию чата"""
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Удалить чат"""
        return super().destroy(request, *args, **kwargs)

    # @action
    # def leave(self, request, *args, **kwargs):
    #     """Выйти из чата"""
    #     ...

    # @action
    # def invite(self, request, *args, **kwargs):
    #     """Пригласить в чат"""
    #     ...

    # @action
    # def expel(self, request, *args, **kwargs):
    #     """Исключить из чата"""
    #     ...
