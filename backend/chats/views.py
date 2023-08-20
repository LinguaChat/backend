"""View-функции приложения chats."""

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chats.models import Chat
from chats.serializers import (ChatListSerializer, ChatSerializer,
                               GroupChatCreateSerializer, MessageSerializer)
from core.pagination import LimitPagination

# from core.permissions import ActiveChatOrReceiverOnly

User = get_user_model()


@extend_schema(tags=['chats'])
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
    # search_fields = (
    #     'members__username', 'members__first_name'
    # )
    ordering = ('-date_created',)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.request.user.chats.all()
        return Chat.objects.none()

    def get_permissions(self):
        # if self.action == 'send_message':
        #     return (ActiveChatOrReceiverOnly(),)
        return super().get_permissions()

    def get_serializer_class(self):
        match self.action:
            case 'create':
                return GroupChatCreateSerializer
            case 'list':
                return ChatListSerializer
            case _:
                return ChatSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        """Просмотреть свои чаты"""
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """Создать групповой чат"""
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Просмотреть чат"""
        return super().retrieve(request, *args, **kwargs)

    # @action(detail=True, methods=['post'])
    # def clear(self, request, *args, **kwargs):
    #     """Очистить сообщения чата"""
    #     chat = self.get_object()
    #     chat.messages.all().delete()

    #     return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Отправить сообщение в чат"""
        chat = self.get_object()
        serializer = MessageSerializer(
            data=request.data,
            context={'request': request}
        )
        if chat.is_user_blocked(request.user):
            return Response(
                {"detail": "Вы заблокированы в этом чате"
                 " и не можете отправлять сообщения."},
                status=status.HTTP_403_FORBIDDEN
            )

        if serializer.is_valid():
            serializer.save(chat=chat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def block_user(self, request, pk=None):
        """Блокировка пользователя в чате"""
        chat = self.get_object()
        user_slug = request.data.get('slug')
        user_to_block = get_object_or_404(User, slug=user_slug)

        if request.user == user_to_block:
            return Response(
                {"detail": "Нельзя заблокировать самого себя."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if chat.members.filter(id=user_to_block.id).exists():
            if user_to_block in chat.blocked_users.all():
                return Response(
                    {"detail": "Пользователь уже заблокирован в этом чате."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            chat.blocked_users.add(user_to_block)
            return Response(
                {"detail": "Пользователь заблокирован в этом чате."},
                status=status.HTTP_201_CREATED
            )

        return Response(
            {"detail": "Пользователь не является участником чата"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def unblock_user(self, request, pk=None):
        """
        Разблокировка пользователя в чате
        """
        chat = self.get_object()
        user_slug = request.data.get('slug')
        user_to_unblock = get_object_or_404(User, slug=user_slug)

        if request.user == user_to_unblock:
            return Response(
                {"detail": "Нельзя разблокировать самого себя"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if chat.members.filter(id=user_to_unblock.id).exists():
            if user_to_unblock in chat.blocked_users.all():
                chat.blocked_users.remove(user_to_unblock)
                return Response(
                    {"detail": "Пользователь разблокирован в этом чате"},
                    status=status.HTTP_200_OK
                )

            return Response(
                {"detail": "Пользователь не заблокирован в этом чате"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "Пользователь не является участником чата"},
            status=status.HTTP_400_BAD_REQUEST
        )
