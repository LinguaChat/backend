"""View-функции приложения chats."""

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chats.models import Chat, Message, PersonalChat
from chats.serializers import (ChatListSerializer, ChatSerializer,
                               ChatStartSerializer, MessageSerializer)
from core.pagination import LimitPagination

# from core.permissions import ActiveChatOrReceiverOnly

User = get_user_model()


@extend_schema(tags=['chats'])
@extend_schema_view(
    list=extend_schema(
        summary='Просмотреть список чатов',
        description=(
            'Просмотреть список всех своих личных чатов'
        ),
    ),
    retrieve=extend_schema(
        summary='Просмотреть чат',
        description='Просмотреть чат и историю сообщений',
    ),
    start_personal_chat=extend_schema(
        summary='Начать чат с пользователем',
        description='Начать чат с пользователем, отправить первое сообщение',
    ),
    send_message=extend_schema(
        summary='Отправить сообщение',
        description='Отправить сообщение в чат',
    ),
)
class ChatViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    serializer_class = ChatSerializer
    http_method_names = ['get', 'post', 'head', 'put']
    permission_classes = [
        IsAuthenticated,
    ]
    pagination_class = LimitPagination
    filter_backends = [
        filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend
    ]
    search_fields = (
        'initiator__username', 'initiator__first_name',
        'receiver__username', 'receiver__first_name',
    )
    ordering = ('-date_created',)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return PersonalChat.objects.filter(
                Q(initiator=self.request.user) |
                Q(receiver=self.request.user)
            )
        return Chat.objects.none()

    def get_permissions(self):
        # if self.action == 'send_message':
        #     return (ActiveChatOrReceiverOnly(),)
        return super().get_permissions()

    def get_serializer_class(self):
        match self.action:
            case 'list':
                return ChatListSerializer
            case 'send_message':
                return MessageSerializer
            case 'start_personal_chat':
                return ChatStartSerializer
        return ChatSerializer

    def list(self, request, *args, **kwargs):
        """Просмотреть свои чаты"""
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Просмотреть чат"""
        return super().retrieve(request, *args, **kwargs)

    @action(
        methods=['post'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=ChatStartSerializer,
        url_path='start-personal-chat'
    )
    def start_personal_chat(self, request, slug=None):
        """Создание личного чата с пользователем."""
        current_user = request.user
        serializer = self.get_serializer(data={
            **request.data
        })
        serializer.is_valid(raise_exception=True)
        user_slug = serializer.data["receiver"]
        user = get_object_or_404(User, slug=user_slug)
        chat = PersonalChat.objects.filter(
            Q(initiator=current_user, receiver=user) |
            Q(initiator=user, receiver=current_user)
        )

        if chat.exists():
            return Response(
                {'message': f'Чат с пользователем {user} уже создан.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        chat = PersonalChat.objects.create(
            initiator=current_user,
            receiver=user
        )
        message_text = serializer.data['message']
        Message.objects.create(
            sender=current_user,
            text=message_text,
            chat=chat
        )
        return Response(
            ChatSerializer(chat).data,
            status=status.HTTP_201_CREATED
        )

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(IsAuthenticated,),
        serializer_class=MessageSerializer,
        url_path='send-message'
    )
    def send_message(self, request, pk=None):
        """Отправить сообщение в чат"""
        chat = self.get_object()

        serializer = self.get_serializer(
            data={**request.data},
            # Передаем chat через контекст
            context={'request': request, 'chat': chat}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()  # Сохраняем сообщение и получаем его объект

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "general",
            {
                "type": "chat_message",
                "message": serializer['text']
            }
        )
        return Response(
            ChatSerializer(chat).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['put'])
    def update_message(self, request, pk=None):
        """Обновить сообщение в чате"""
        message_id = request.data.get('message_id')
        chat = self.get_object()

        try:
            message = chat.messages.get(id=message_id)
        except Message.DoesNotExist:
            return Response(
                {"detail": "Message not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MessageSerializer(
            instance=message,
            data=request.data,
            context={'request': request},
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def view_chat(self, request, pk=None):
        """Просмотреть чат и обновить статус 'прочитано' для получателя"""
        chat = self.get_object()

        user = self.request.user

        if chat.initiator == user or chat.receiver == user:
            for message in chat.messages.exclude(read_by=user):
                message.read_by.add(user)
            return Response({"detail": "Chat read status updated."})
        else:
            return HttpResponseForbidden(
                "You don't have permission to access this chat."
            )
