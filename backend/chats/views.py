"""View-функции приложения chats."""

from django.contrib.auth import get_user_model
from django.utils import timezone

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
        return ChatSerializer

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

        if serializer.is_valid():
            serializer.save(chat=chat)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def view_chat(self, request, pk=None):
        """Просмотреть чат и обновить статус 'прочитано' для получателя"""
        chat = self.get_object()

        # Получаем текущего пользователя
        user = self.request.user

        # Обновляем статус 'прочитано' для всех сообщений в чате, если текущий пользователь не отправитель
        if chat.members.filter(id=user.id).exists():
            for message in chat.messages.exclude(read_by=user):
                message.read_by.add(user)
            return Response({"detail": "Chat read status updated."})
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
