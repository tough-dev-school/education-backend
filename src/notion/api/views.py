from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from notion.api.serializers import NotionPageSerializer
from notion.client import NotionClient


class NotionPageView(APIView):
    serializer_class = NotionPageSerializer
    permission_classes = [permissions.IsAdminUser]

    def get(self, request: Request, *args, **kwargs) -> Response:
        page = self.notion.fetch_page_recursively(self.kwargs['page_id'])

        return Response(
            data=NotionPageSerializer(page).data,
            status=200,
        )

    @property
    def notion(self) -> NotionClient:
        return NotionClient()
