from rest_framework import permissions


class IsStaffOrSuperuser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return request.user.is_staff or request.user.is_superuser
        return False