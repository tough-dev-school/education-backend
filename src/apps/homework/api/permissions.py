from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.homework.models import Answer, Reaction


class AuthorOrReadonly(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: APIView, obj: Answer | Reaction) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user


class IsEditable(permissions.BasePermission):
    def has_object_permission(self, request: Request, view: APIView, answer: Answer) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return True

        return answer.is_editable
