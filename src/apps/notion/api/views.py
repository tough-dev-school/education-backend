from typing import Any

from django.contrib.admin.models import CHANGE
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from apps.lms.api.serializers import BreadcrumbsSerializer
from apps.notion.api.serializers import NotionCacheEntryStatusSerializer, NotionPageSerializer
from apps.notion.api.throttling import NotionThrottle
from apps.notion.breadcrumbs import get_lesson
from apps.notion.cache import get_cached_page_or_fetch
from apps.notion.id import uuid_to_id
from apps.notion.models import Material, NotionCacheEntryStatus
from apps.notion.tasks import update_cache
from core.tasks import write_admin_log
from core.views import AuthenticatedAPIView, AdminAPIView


class MaterialStatusView(AdminAPIView, RetrieveAPIView):
    """Get material update status"""

    queryset = NotionCacheEntryStatus.objects.all()
    serializer_class = NotionCacheEntryStatusSerializer

    def get_object(self) -> NotionCacheEntryStatus:
        material = get_object_or_404(Material, page_id=self.kwargs["page_id"])

        return get_object_or_404(NotionCacheEntryStatus, page_id=material.page_id)


class MaterialUpdateView(AdminAPIView):
    """Trigger material update"""

    def get_object(self) -> Material:
        return get_object_or_404(Material, page_id=self.kwargs["page_id"])

    @extend_schema(request=None, responses={200: None})
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        material = self.get_object()

        self.write_admin_log(material)
        self.update_cache(material)

        return Response(status=200)

    @staticmethod
    def no_update_pending(material: Material) -> bool:
        try:
            status = NotionCacheEntryStatus.objects.get(page_id=material.page_id)
            return (status.fetch_started is None) or (status.fetch_complete is not None)
        except NotionCacheEntryStatus.DoesNotExist:
            return False

    def write_admin_log(self, material: Material) -> None:
        write_admin_log.delay(
            action_flag=CHANGE,
            change_message="Material update triggered",
            model="notion.Material",
            object_id=material.id,
            user_id=self.request.user.id,
        )

    def update_cache(self, material: Material) -> None:
        update_cache.delay(page_id=material.page_id)


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
