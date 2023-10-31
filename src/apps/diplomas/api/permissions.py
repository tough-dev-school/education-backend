from typing import Any

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView


class DiplomaPermission(permissions.DjangoObjectPermissions):
    """Allow every (even anonymous) user to access particular diplomas.
    Use default Django permissions for any other action
    """

    def has_permission(self, request: Request, view: APIView) -> bool:
        if view.action == "retrieve":  # type: ignore
            return True

        return super().has_permission(request, view)

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        return super().has_object_permission(request, view, obj)
