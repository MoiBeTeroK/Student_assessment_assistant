from rest_framework.permissions import BasePermission


def is_admin(user):
    return user.groups.filter(name='admin').exists()


def is_teacher(user):
    return user.groups.filter(name='teacher').exists()


class IsAdmin(BasePermission):
    """Только администраторы"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and is_admin(request.user)


class IsAdminOrSelf(BasePermission):
    """Админ — всё, преподаватель — только себя"""
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if is_admin(request.user):
            return True
        # Преподаватель видит только свой объект
        return obj == request.user or getattr(obj, 'user', None) == request.user