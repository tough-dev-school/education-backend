from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from app.views import AuthenticatedAPIView
from notion.api.serializers import NotionPageSerializer
from notion.client import NotionClient
from notion.helpers import uuid_to_id
from notion.models import Material
from studying.models import Study


class NotionMaterialView(AuthenticatedAPIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        material = self.get_material()

        page = self.notion.fetch_page_recursively(material.page_id)

        return Response(
            data=NotionPageSerializer(page).data,
            status=200,
        )

    def get_material(self) -> Material:
        queryset = self.get_queryset()
        return get_object_or_404(queryset, page_id=self.page_id)

    def get_queryset(self) -> QuerySet[Material]:
        if self.request.user.is_superuser or self.request.user.has_perm('notion.see_all_materials'):
            return Material.objects.all()

        available_courses = Study.objects.filter(student=self.request.user).values('course')
        return Material.objects.filter(active=True, course__in=available_courses)

    @property
    def notion(self) -> NotionClient:
        return NotionClient()

    @property
    def page_id(self) -> str:
        return uuid_to_id(self.kwargs['page_id'])
