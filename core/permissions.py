from rest_framework import permissions


class ActiveChatOrReceiverOnly(permissions.BasePermission):
    """
    Разрешение на редактирование и удаление только для владельца.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            obj.members.filter(id=request.user.id).exists()
            and (
            obj.is_active
            or not obj.members_info.get(member=request.user).is_creator)
        )
