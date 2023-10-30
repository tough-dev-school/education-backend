from typing import Any

from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from django.db.models import QuerySet

from apps.notion.api.serializers import NotionPageSerializer
from apps.notion.api.throttling import NotionThrottle
from apps.notion.cache import get_cached_page
from apps.notion.helpers import uuid_to_id
from apps.notion.models import Material
from core.views import AuthenticatedAPIView


class NotionMaterialView(AuthenticatedAPIView):
    throttle_classes = [NotionThrottle]

    def get(self, request: Request, *args: Any, **kwargs: dict[str, Any]) -> Response:
        material = self.get_material()

        if material is None:
            raise NotFound()

        page = get_cached_page(material.page_id)

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
