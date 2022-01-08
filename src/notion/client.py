import httpx
from django.conf import settings

from notion.block import NotionBlockList
from notion.page import NotionPage
from notion.types import BlockId


class NotionError(Exception):
    ...


class NotionClient:
    def fetch_page(self, page_id: str) -> NotionPage:
        """Fetch notion page"""
        response = self.fetch(
            resource='loadCachedPageChunk',
            request_body={
                'page': {'id': self.id_to_uuid(page_id)},
                'limit': 100,
                'cursor': {'stack': []},
                'chunkNumber': 0,
                'verticalColumns': False,
            },
        )

        return NotionPage.from_api_response(response)

    def fetch_blocks(self, blocks: list[BlockId]) -> NotionBlockList:
        """Fetch a list of notion blocks"""
        response = self.fetch(
            resource='syncRecordValues',
            request_body={
                'requests': [{'id': block, 'table': 'block', 'version': -1} for block in blocks],
            },
        )

        return NotionBlockList.from_api_response(response['recordMap']['block'])

    def fetch(self, resource: str, request_body: dict) -> dict:
        response = httpx.post(
            url=f'https://www.notion.so/api/v3/{resource}',
            cookies={'token_v2': settings.NOTION_TOKEN},
            json=request_body,
            headers={
                'content-type': 'application/json',
            },
        )

        if response.status_code != 200:
            raise NotionError(f'HTTP Error {response.status_code} fetching notion resouce {resource}: {response.text}')

        return response.json()

    @staticmethod
    def id_to_uuid(id: str) -> str:
        normalized = id.replace('-', '')
        return f'{normalized[0:8]}-{normalized[8:12]}-{normalized[12:16]}-{normalized[16:20]}-{normalized[20:]}'
