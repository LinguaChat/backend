"""Кастомные разрешения."""

from rest_framework import permissions


class ActiveChatOrReceiverOnly(permissions.BasePermission):
    #     """
    #     Разрешение на отправку сообщений для участников активного чата
    #     или только для получателя.
    #     """

    #     def has_permission(self, request, view):
    #         return request.user.is_authenticated

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            obj.is_active or obj.receiver == request.user
        )


class IsAdminOrModeratorReadOnly(permissions.BasePermission):
    """
    Разрешение на просмотр Администраторам или Модераторам.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            user = request.user
            return (
                user.is_staff or
                user.role == 'moderator' or
                user.role == 'admin'
            )
        return True


class CanAccessProfileDetails(permissions.BasePermission):
    """
    Проверяет, разрешено ли пользователю
    просматривать детали профиля другого пользователя.
    """

    message = "Просмотр профиля заблокирован для данного пользователя."

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_authenticated:
            if user == obj:
                return True
            if user.blacklist_entries_received.filter(user=obj).exists():
                return False
        return True
