import contextlib
from dataclasses import dataclass

from notion.block import NotionBlock
from notion.block import NotionBlockList
from notion.exceptions import NotionResponseError
from notion.exceptions import NotSharedForWeb


@dataclass
class NotionPage:
    blocks: NotionBlockList

    def to_json(self) -> dict:
        return {"blocks": [block.to_json() for block in self.blocks]}

    @classmethod
    def from_json(cls, data: dict) -> "NotionPage":
        blocks = NotionBlockList([NotionBlock.from_json(block_dict) for block_dict in data["blocks"]])
        return cls(blocks=blocks)

    @classmethod
    def from_api_response(cls, api_response: dict) -> "NotionPage":
        if "errorId" in api_response:
            raise NotionResponseError(f"Notion response error. {api_response['name']}: {api_response['message']}")

        if "block" not in api_response["recordMap"]:
            raise NotSharedForWeb()

        return cls(
            blocks=NotionBlockList.from_api_response(api_response["recordMap"]["block"]),
        )

    @property
    def title(self) -> str | None:
        if self.blocks.first_page_block is not None:
            with contextlib.suppress(KeyError, IndexError):
                return self.blocks.first_page_block.data["value"]["properties"]["title"][0][0]
