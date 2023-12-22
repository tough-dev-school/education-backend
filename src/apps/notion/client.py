from collections.abc import Iterable
from typing import TYPE_CHECKING

import httpx
from sentry_sdk import add_breadcrumb

from django.conf import settings

from apps.notion.exceptions import HTTPError
from apps.notion.helpers import id_to_uuid
from apps.notion.page import NotionPage
from apps.notion.types import BlockId

if TYPE_CHECKING:
    from apps.notion.block import NotionBlockList


class NotionClient:
    """Client for private notion.so API, inspired by https://github.com/splitbee/notion-api-worker"""

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

        page.save_assets()
        return page

    def fetch_page(self, page_id: str) -> NotionPage:
        """Fetch notion page"""
        response = self.fetch(
            resource="loadPageChunk",
            request_body={
                "page": {"id": id_to_uuid(page_id)},
                "limit": 30,
                "cursor": {"stack": []},
                "chunkNumber": 0,
                "verticalColumns": False,
            },
        )

        return NotionPage.from_api_response(response)

    def fetch_blocks(self, blocks: Iterable[BlockId]) -> "NotionBlockList":
        """Fetch a list of notion blocks"""
        from apps.notion.block import NotionBlockList

        response = self.fetch(
            resource="syncRecordValues",
            request_body={
                "requests": [{"id": block, "table": "block", "version": -1} for block in blocks],
            },
        )

        return NotionBlockList.from_api_response(response["recordMap"]["block"])

    @staticmethod
    def fetch(resource: str, request_body: dict) -> dict:
        """Query notion through our middleware"""
        add_breadcrumb(category="http", message=f"Sending notion request for {resource}", level="debug", data=request_body)

        client = httpx.Client(
            http2=True,
        )
        response = client.post(
            url=f"{settings.NOTION_MIDDLEWARE_URL}/v1/notion/{resource}/",
            headers={
                "content-type": "application/json",
            },
            json=request_body,
            timeout=settings.NOTION_MIDDLEWARE_TIMEOUT,
        )

        if response.status_code != 200:
            raise HTTPError(f"{ response.http_version } error {response.status_code} fetching notion resouce {resource}: {response.text}")

        notion_response = response.json()

        add_breadcrumb(category="http", message=f"Got notion response for {resource}", level="debug", data=notion_response)

        return notion_response

    @staticmethod
    def fetch_asset(url: str) -> bytes:
        """Fetch asset through our middleware"""
        add_breadcrumb(category="http", message="Fetching notion asset", level="debug", data={url: url})

        client = httpx.Client(
            http2=True,
        )
        response = client.post(
            url=f"{settings.NOTION_MIDDLEWARE_URL}/v1/asset/",
            json={
                "url": url,
            },
            timeout=settings.NOTION_MIDDLEWARE_ASSET_FETCHING_TIMEOUT,
        )

        if response.status_code != 200:
            raise HTTPError(f"{ response.http_version } error {response.status_code} fetching asset {url}: {response.text}")

        return response.content
