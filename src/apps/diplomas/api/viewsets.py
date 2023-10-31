from typing import Any

from rest_framework.exceptions import MethodNotAllowed
from rest_framework.request import Request

from django.db.models import QuerySet

from apps.diplomas.api import serializers
from apps.diplomas.api.permissions import DiplomaPermission
from apps.diplomas.models import Diploma
from core.api.mixins import DisablePaginationWithQueryParamMixin
from core.viewsets import AppViewSet


class DiplomaViewSet(DisablePaginationWithQueryParamMixin, AppViewSet):
    queryset = Diploma.objects.for_viewset()
    lookup_field = "slug"
    serializer_class = serializers.DiplomaSerializer
    serializer_action_classes = {
        "create": serializers.DiplomaCreateSerializer,
        "retrieve": serializers.DiplomaRetrieveSerializer,
    }
    permission_classes = [DiplomaPermission]

    def get_queryset(self) -> QuerySet:
        """Filter diplomas only for current user"""
        queryset: QuerySet[Diploma] = super().get_queryset()

        if self.action != "retrieve" and not self.request.user.has_perm("diplomas.access_all_diplomas"):
            queryset = queryset.for_user(self.request.user)  # type: ignore

        return queryset

    def update(self, request: Request, **kwargs: dict[str, Any]) -> None:  # type: ignore
        raise MethodNotAllowed(request.method)  # type: ignore

    def destroy(self, request: Request, **kwargs: dict[str, Any]) -> None:  # type: ignore
        raise MethodNotAllowed(request.method)  # type: ignore
