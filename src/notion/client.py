import httpx
from collections.abc import Iterable
from django.conf import settings

from notion.block import NotionBlockList
from notion.helpers import id_to_uuid
from notion.page import NotionPage
from notion.types import BlockId


class NotionError(Exception):
    ...


class NotionClient:
    """Client for private notion.so API, inspired by https://github.com/splitbee/notion-api-worker
    """
    def __init__(self) -> None:
        self.attempted_blocks: list[BlockId] = list()

    def fetch_page_recursively(self, page_id: str) -> NotionPage:
        """Fetch page with all underliying non-page blocks"""
        self.attempted_blocks = list()
        page = self.fetch_page(page_id)

        while True:
            page_blocks = page.blocks.get_underlying_block_ids()

            new_blocks_to_fetch = [block for block in page_blocks if block not in self.attempted_blocks]

            if len(new_blocks_to_fetch) == 0:
                break

            self.attempted_blocks += new_blocks_to_fetch  # save blocks that we already have tried to fetch, to make sure we will not request them again even if notion does not return them
            page.blocks += self.fetch_blocks(new_blocks_to_fetch)

        return page

    def fetch_page(self, page_id: str) -> NotionPage:
        """Fetch notion page"""
        response = self.fetch(
            resource='loadPageChunk',
            request_body={
                'page': {'id': id_to_uuid(page_id)},
                'limit': 100,
                'cursor': {'stack': []},
                'chunkNumber': 0,
                'verticalColumns': False,
            },
        )

        return NotionPage.from_api_response(response)

    def fetch_blocks(self, blocks: Iterable[BlockId]) -> NotionBlockList:
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
