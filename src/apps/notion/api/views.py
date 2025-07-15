from typing import Any

from django.db.models import QuerySet
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from apps.lms.api.serializers import BreadcrumbsSerializer
from apps.notion.api.serializers import NotionPageSerializer
from apps.notion.api.throttling import NotionThrottle
from apps.notion.breadcrumbs import get_lesson
from apps.notion.cache import get_cached_page_or_fetch
from apps.notion.id import uuid_to_id
from apps.notion.models import Material
from core.views import AuthenticatedAPIView


class MaterialView(AuthenticatedAPIView):
    throttle_classes = [NotionThrottle]

    @extend_schema(
        description="Fetch material",
        responses={
            200: inline_serializer(
                name="MaterialSerilizer",
                fields={
                    "breadcrumbs": BreadcrumbsSerializer(),
                    "content": serializers.DictField(),
                },
            ),
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> Response:
        material = self.get_material()

        if material is None:
            raise NotFound()

        page = get_cached_page_or_fetch(material.page_id)
        lesson = get_lesson(material)

        return Response(
            data={
                "breadcrumbs": BreadcrumbsSerializer(lesson).data if lesson is not None else {},
                "content": NotionPageSerializer(page).data,
            },
            status=200,
        )

    def get_material(self) -> Material | None:
        queryset = self.get_queryset()

        return queryset.get_by_page_id_or_slug(uuid_to_id(self.kwargs["page_id"]))  # type: ignore

    def get_queryset(self) -> QuerySet[Material]:
        if self.request.user.is_superuser or self.request.user.has_perm("notion.see_all_materials"):
            return Material.objects.all()

        return Material.objects.for_student(self.request.user)


class LegacyNotionMaterialView(AuthenticatedAPIView):
    """Legacy API View"""

    serializer_class = NotionPageSerializer()

    def get(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> Response:
        """[DEPRECATED] Fetch notion materials"""
        material = self.get_material()

        if material is None:
            raise NotFound()

        page = get_cached_page_or_fetch(material.page_id)

        return Response(
            data=NotionPageSerializer(page).data,
            status=200,
        )

    def get_material(self) -> Material | None:
        queryset = self.get_queryset()

        return queryset.get_by_page_id_or_slug(self.page_id)  # type: ignore

    def get_queryset(self) -> QuerySet[Material]:
        if self.request.user.is_superuser or self.request.user.has_perm("notion.see_all_materials"):
            return Material.objects.all()

        return Material.objects.for_student(self.request.user)

    @property
    def page_id(self) -> str:
        return uuid_to_id(self.kwargs["page_id"])
