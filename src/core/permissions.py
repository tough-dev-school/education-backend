from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView


class SuperUserOnly(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.user.is_superuser  # type: ignore[union-attr]


__all__ = [
    "AllowAny",
    "IsAuthenticated",
    "SuperUserOnly",
]
