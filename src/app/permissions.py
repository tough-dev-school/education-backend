from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated


class SuperUserOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


__all__ = [
    AllowAny,
    IsAuthenticated,
    SuperUserOnly,
]
