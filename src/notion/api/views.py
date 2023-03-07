from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from django.db.models import QuerySet

from app.views import AuthenticatedAPIView
from notion.api.serializers import NotionPageSerializer
from notion.api.throttling import NotionThrottle
from notion.cache import get_cached_page
from notion.helpers import uuid_to_id
from notion.models import Material
from studying.models import Study


class NotionMaterialView(AuthenticatedAPIView):
    throttle_classes = [NotionThrottle]

    def get(self, request: Request, *args, **kwargs) -> Response:
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

        return queryset.filter(page_id=self.page_id).first()

    def get_queryset(self) -> QuerySet[Material]:
        if self.request.user.is_superuser or self.request.user.has_perm("notion.see_all_materials"):
            return Material.objects.all()

        available_courses = Study.objects.filter(student=self.request.user).values("course")
        return Material.objects.filter(active=True, course__in=available_courses)

    @property
    def page_id(self) -> str:
        return uuid_to_id(self.kwargs["page_id"])
