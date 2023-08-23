"""View-функции приложения chats."""

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chats.models import Chat, PersonalChat, Message
from chats.serializers import (ChatListSerializer, ChatSerializer,
                               ChatStartSerializer, MessageSerializer)
from core.pagination import LimitPagination
# from core.permissions import ActiveChatOrReceiverOnly

User = get_user_model()


@extend_schema(tags=['chats'])
class ChatViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
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
        # 'members__username', 'members__first_name',
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
        else:
            chat = PersonalChat.objects.create(
                initiator=current_user,
                receiver=user
            )
            message_text = serializer.data['message']
            message = Message.objects.create(
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
        serializer = self.get_serializer(data={
            # 'chat': pk,
            # 'sender': request.user,
            **request.data
        })
        serializer.is_valid(raise_exception=True)
        serializer.save(chat=chat, sender=request.user)
        return Response(
            ChatSerializer(chat).data,
            status=status.HTTP_201_CREATED
        )
