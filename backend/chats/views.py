"""View-функции приложения chats."""

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from chats.models import GroupChat, Message, PersonalChat
from chats.serializers import (ChatListSerializer, ChatSerializer,
                               ChatStartSerializer, GroupChatCreateSerializer,
                               GroupChatSerializer, MessageSerializer)
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
    http_method_names = ['get', 'post', 'head']
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
        return PersonalChat.objects.none()

    def get_group_queryset(self):
        if self.request.user.is_authenticated:
            return GroupChat.objects.filter(members=self.request.user)
        return GroupChat.objects.none()

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
            case 'start_group_chat':
                return GroupChatCreateSerializer
            case 'retrieve':
                return GroupChatSerializer
        return ChatSerializer

    def list(self, request, *args, **kwargs):
        personal_chats = self.get_queryset()
        group_chats = self.get_group_queryset()

        all_chats = list(personal_chats) + list(group_chats)

        sorted_chats = sorted(
            all_chats, key=lambda chat: chat.date_created, reverse=True)

        serializer = ChatListSerializer(sorted_chats, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        chat_id = self.kwargs['pk']
        try:
            chat = PersonalChat.objects.get(pk=chat_id)
        except PersonalChat.DoesNotExist:
            try:
                chat = GroupChat.objects.get(pk=chat_id)
            except GroupChat.DoesNotExist:
                return Response(
                    {"detail": "Чат не найден."},
                    status=status.HTTP_404_NOT_FOUND
                )

        serializer = self.get_serializer(chat)
        return Response(serializer.data)

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
        detail=False,
        permission_classes=(IsAuthenticated,),
        serializer_class=GroupChatCreateSerializer,
        url_path='start-group-chat'
    )
    def start_group_chat(self, request):
        """Создание группового чата."""
        current_user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        chat_name = serializer.validated_data["name"]
        existing_chat = GroupChat.objects.filter(name=chat_name).first()

        if existing_chat:
            return Response(
                {"detail": "Чат с таким названием уже существует."},
                status=status.HTTP_400_BAD_REQUEST
            )
        group_chat = GroupChat.objects.create(
            initiator=current_user,
            name=serializer.validated_data["name"]
        )
        group_chat.members.set(serializer.validated_data["members"])
        message_text = serializer.validated_data.get("message")
        if message_text:
            Message.objects.create(
                sender=current_user,
                text=message_text,
                chat=group_chat
            )

        return Response(
            GroupChatSerializer(group_chat).data,
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
            context={'request': request, 'chat': chat}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save(chat=chat, sender=request.user)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{chat.pk}",
            {
                "type": "chat_message",
                "message": serializer['text']
            }
        )
        return Response(
            ChatSerializer(chat).data,
            status=status.HTTP_201_CREATED
        )

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

        if chat.initiator == request.user or chat.receiver == request.user:
            if (
                user_to_block == chat.initiator
                    or user_to_block == chat.receiver
            ):
                # if chat.members.filter(id=user_to_block.id).exists():
                if user_to_block in chat.blocked_users.all():
                    return Response(
                        {"detail": "Пользователь уже заблокирован "
                         "в этом чате."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                chat.blocked_users.add(user_to_block)
                # Отправить обновление через веб-сокеты
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"chat_{chat.pk}",
                    {
                        "type": "block_user",
                        "user_slug": user_slug,
                        "blocked": True
                    }
                )

                return Response(
                    {"detail": "Пользователь заблокирован в этом чате."},
                    status=status.HTTP_201_CREATED
                )

            return Response(
                {"detail": "Пользователь не является участником чата"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"detail": "У вас нет прав для блокировки участников этого чата."},
            status=status.HTTP_403_FORBIDDEN
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

        if chat.initiator == request.user or chat.receiver == request.user:
            if (
                user_to_unblock == chat.initiator
                    or user_to_unblock == chat.receiver
            ):
                # if chat.members.filter(id=user_to_unblock.id).exists():
                if user_to_unblock in chat.blocked_users.all():
                    chat.blocked_users.remove(user_to_unblock)

                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        f"chat_{chat.pk}",
                        {
                            "type": "block_user",
                            "user_slug": user_slug,
                            "blocked": False
                        }
                    )
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

        return Response(
            {"detail": "Вы не имеете права "
             "разблокировать участников в этом чате"},
            status=status.HTTP_403_FORBIDDEN
        )
