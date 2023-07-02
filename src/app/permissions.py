from rest_framework.permissions import AllowAny
from rest_framework.permissions import BasePermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView


class SuperUserOnly(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.user.is_superuser


__all__ = [
    "AllowAny",
    "IsAuthenticated",
    "SuperUserOnly",
]
