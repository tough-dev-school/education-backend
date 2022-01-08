from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from notion.api.serializers import NotionPageSerializer
from notion.client import NotionClient


class NotionMaterialView(APIView):
    serializer_class = NotionPageSerializer

    def get(self, request: Request, *args, **kwargs) -> Response:
        page = self.notion.fetch_page_recursively(self.get_page_id())

        return Response(
            data=NotionPageSerializer(page).data,
            status=200,
        )

    def get_page_id(self) -> str:
        return NotionClient.id_to_uuid(self.kwargs['page_id'])

    @property
    def notion(self) -> NotionClient:
        return NotionClient()
