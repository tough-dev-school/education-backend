from rest_framework.permissions import AllowAny
from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated


class SuperUserOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


__all__ = [
    "AllowAny",
    "IsAuthenticated",
    "SuperUserOnly",
]
