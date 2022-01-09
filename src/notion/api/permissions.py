from rest_framework.permissions import DjangoModelPermissions
from rest_framework.request import Request
from rest_framework.views import APIView

from notion.models import Material


class NotionMaterialPermission(DjangoModelPermissions):
    def has_object_permission(self, request: Request, view: APIView, obj: Material) -> bool:
        pass
