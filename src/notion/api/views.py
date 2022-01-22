from typing import Any, Optional

from django.db.models import QuerySet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response

from app.views import AuthenticatedAPIView
from notion.api.serializers import NotionPageSerializer
from notion.api.throttling import NotionThrottle
from notion.client import NotionClient
from notion.helpers import uuid_to_id
from notion.models import Material
from notion.page import NotionPage
from studying.models import Study


class NotionMaterialView(AuthenticatedAPIView):
    throttle_classes = [NotionThrottle]

    @method_decorator(cache_control(private=True, max_age=3600))
    def get(self, request: Request, *args, **kwargs) -> Response:
        material = self.get_material()

        if material is None:
            raise NotFound()

        page = self.notion.fetch_page_recursively(material.page_id)

        return Response(
            data=NotionPageSerializer(page).data,
            status=200,
            headers=self.get_headers(page),
        )

    def get_material(self) -> Optional[Material]:
        queryset = self.get_queryset()

        return queryset.filter(page_id=self.page_id).first()

    def get_queryset(self) -> QuerySet[Material]:
        if self.request.user.is_superuser or self.request.user.has_perm('notion.see_all_materials'):
            return Material.objects.all()

        available_courses = Study.objects.filter(student=self.request.user).values('course')
        return Material.objects.filter(active=True, course__in=available_courses)

    @staticmethod
    def get_headers(page: NotionPage) -> dict:
        headers: dict[str, Any] = dict()

        if page.last_modified is not None:
            headers['last-modified'] = page.last_modified.strftime('%a, %d %b %Y %H:%M:%S %Z')

        return headers

    @property
    def notion(self) -> NotionClient:
        return NotionClient()

    @property
    def page_id(self) -> str:
        return uuid_to_id(self.kwargs['page_id'])
