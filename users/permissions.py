from rest_framework.permissions import BasePermission

MODERATOR_GROUP_NAMES = ["moderators", "Модераторы"]


def is_moderator(user) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    return user.groups.filter(name__in=MODERATOR_GROUP_NAMES).exists()


class IsModer(BasePermission):
    """
    Пользователь в группе модераторов (или staff/superuser).
    """

    def has_permission(self, request, view):
        return is_moderator(request.user)


class IsOwner(BasePermission):
    """
    Владелец объекта (для Course/Lesson с полем owner).
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        if hasattr(obj, "owner"):
            return obj.owner == user

        if hasattr(obj, "user"):
            return obj.user == user

        return False


class IsSelf(BasePermission):
    """
    Пользователь обращается к своему профилю (UserViewSet).
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        return obj == user
