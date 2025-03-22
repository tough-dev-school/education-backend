import contextlib
from dataclasses import dataclass

from apps.notion.block import NotionBlock, NotionBlockList
from apps.notion.exceptions import NotionResponseError, NotSharedForWeb
from apps.notion.types import BlockId


@dataclass
class NotionPage:
    id: BlockId
    blocks: NotionBlockList

    def to_json(self) -> dict:
        return {"blocks": [block.to_json() for block in self.blocks]}

    @classmethod
    def from_json(cls, data: dict, kwargs: dict[str, str | BlockId] | None = None) -> "NotionPage":
        kwargs = kwargs if kwargs is not None else dict()
        blocks = NotionBlockList([NotionBlock.from_json(block_dict) for block_dict in data["blocks"]])
        return cls(blocks=blocks, **kwargs)

    @classmethod
    def from_api_response(cls, response: dict, kwargs: dict[str, str | BlockId] | None = None) -> "NotionPage":
        kwargs = kwargs if kwargs is not None else dict()
        if "errorId" in response:
            raise NotionResponseError(f"Notion response error. {response['name']}: {response['message']}")

        if "block" not in response["recordMap"]:
            raise NotSharedForWeb()

        return cls(
            blocks=NotionBlockList.from_api_response(response["recordMap"]["block"]),
            **kwargs,
        )

    @property
    def title(self) -> str | None:
        if self.blocks.first_page_block is not None:
            with contextlib.suppress(KeyError, IndexError):
                return self.blocks.first_page_block.data["value"]["properties"]["title"][0][0]

    def after_fetch(self) -> None:
        """Called after page fetching or updating"""
        self.save_assets()

    def save_assets(self) -> None:
        """Save assets from all underlying blocks"""
        for block in self.blocks:
            block.save_assets()
