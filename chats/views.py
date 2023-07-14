"""View-функции для приложения chats."""

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated

from core.pagination import LimitPagination
from core.permissions import ActiveChatOrReceiverOnly

from .serializers import ChatListSerializer, ChatSerializer

# from rest_framework.decorators import action

User = get_user_model()


class ChatViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSerializer
    http_method_names = ['get', 'post', 'head']
    permission_classes = [
        IsAuthenticated,
    ]
    pagination_class = LimitPagination
    filter_backends = [
        filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend
    ]
    search_fields = (
        'members__username', 'members__first_name'
    )
    ordering = ('-date_created',)

    def get_queryset(self):
        return self.request.user.chats.all()

    def get_permissions(self):
        if self.action == 'send_message':
            return (ActiveChatOrReceiverOnly(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'list':
            return ChatListSerializer
        return ChatSerializer

    def list(self, request, *args, **kwargs):
        """Просмотреть свои чаты"""
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Начать чат"""
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Просмотреть чат"""
        return super().retrieve(request, *args, **kwargs)

    # @action
    # def clear(self, request, *args, **kwargs):
    #     """Очистить сообщения чата"""
    #     ...

    # @action
    # def send_message(self, request, *args, **kwargs):
    #     """Отправить сообщение в чат"""
    #     ...
