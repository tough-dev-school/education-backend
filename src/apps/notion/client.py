from collections.abc import Iterable
from typing import TYPE_CHECKING

from apps.notion import http
from apps.notion.id import id_to_uuid

if TYPE_CHECKING:
    from apps.notion.block import NotionBlockList
    from apps.notion.page import NotionPage
    from apps.notion.types import NotionId


class NotionClient:
    """Client for private notion.so API, inspired by https://github.com/splitbee/notion-api-worker"""

    def __init__(self) -> None:
        self.attempted_blocks: list[NotionId] = list()

    def fetch_page(self, page_id: str) -> "NotionPage":
        """Fetch page with all underliying non-page blocks"""
        self.attempted_blocks = list()

        page = self.fetch_page_root(page_id)
        self.fetch_page_blocks(page)
        page.after_fetch()  # call actions that should happen after page fetch

        return page

    def fetch_page_blocks(self, page: "NotionPage") -> None:
        while True:
            page_blocks = page.blocks.get_underlying_block_ids()

            new_blocks_to_fetch = [block for block in page_blocks if block not in self.attempted_blocks]

            if len(new_blocks_to_fetch) == 0:
                break

            self.attempted_blocks += new_blocks_to_fetch  # save blocks that we already have tried to fetch, to make sure we will not request them again even if notion does not return them
            page.blocks += self.fetch_blocks(new_blocks_to_fetch)

    def fetch_page_root(self, page_id: "NotionId") -> "NotionPage":
        """Fetch root page data, without underlying blocks"""
        from apps.notion.page import NotionPage

        response = http.fetch(
            resource="loadPageChunk",
            request_body={
                "page": {"id": id_to_uuid(page_id)},
                "limit": 30,
                "cursor": {"stack": []},
                "chunkNumber": 0,
                "verticalColumns": False,
            },
        )

        return NotionPage.from_api_response(response=response, kwargs={"id": page_id})

    def fetch_blocks(self, blocks: Iterable["NotionId"]) -> "NotionBlockList":
        """Fetch a list of notion blocks"""
        from apps.notion.block import NotionBlockList

        response = http.fetch(
            resource="syncRecordValues",
            request_body={
                "requests": [{"id": block, "table": "block", "version": -1} for block in blocks],
            },
        )

        return NotionBlockList.from_api_response(response["recordMap"]["block"])
