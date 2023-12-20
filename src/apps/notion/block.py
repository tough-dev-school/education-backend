from collections import UserList
import contextlib
from dataclasses import dataclass
from typing import Generator

from apps.notion import tasks
from apps.notion.assets import get_asset_url
from apps.notion.assets import is_notion_url
from apps.notion.rewrite import apply_our_adjustments
from apps.notion.types import BlockData
from apps.notion.types import BlockFormat
from apps.notion.types import BlockId
from apps.notion.types import BlockProperties
from apps.notion.types import BlockType


@dataclass
class NotionBlock:
    id: BlockId
    data: BlockData

    def to_json(self) -> dict:
        return {"id": self.id, "data": self.data}

    @classmethod
    def from_json(cls, data: dict) -> "NotionBlock":
        return cls(id=data["id"], data=data["data"])

    @property
    def type(self) -> BlockType | None:
        with contextlib.suppress(KeyError):
            return self.data["value"]["type"]

    @property
    def content(self) -> list[BlockId]:
        try:
            return self.data["value"]["content"]
        except KeyError:
            return list()

    @property
    def format(self) -> BlockFormat:
        try:
            return self.data["value"]["format"]
        except KeyError:
            return {}

    @property
    def properties(self) -> BlockProperties:
        result: BlockProperties = dict()
        if "value" in self.data:
            for property_name, value in self.data["value"].get("properties", {}).items():
                result[property_name] = value[0][0]  # type: ignore

        return result

    def get_data(self) -> BlockData:
        return apply_our_adjustments(self.data)

    def get_assets_to_save(self) -> list[str]:  # NOQA: CCR001
        """Returns a list of asset urls as defined in notion response
        Returnes only assets to fetch

        """
        if self.type == "image":
            return [self.properties["source"]]

        if self.type == "page":
            result = list()
            for key in ("page_icon", "page_cover"):
                if key in self.format and is_notion_url(self.format[key]):  # type: ignore
                    result.append(self.format[key])  # type: ignore

            return result

        return []

    def save_assets(self) -> None:
        """Asynchronously download and save all assets in the block"""
        for asset in self.get_assets_to_save():
            tasks.save_asset.apply_async(
                kwargs={
                    "original_url": asset,
                    "url": get_asset_url(asset, self.data),
                },
            )


class NotionBlockList(UserList[NotionBlock]):
    @classmethod
    def from_json(cls, data: dict) -> "NotionBlockList":
        blocks = [NotionBlock.from_json(block_dict) for block_dict in data]
        return cls(blocks)

    def ordered(self) -> "NotionBlockList":
        if self.first_page_block is None:
            return self

        result = self.__class__([self.first_page_block])

        for block in self.data:
            if block.id is None or block.id != self.first_page_block.id:
                result.append(block)

        return result

    @classmethod
    def from_api_response(cls, api_response: dict[str, BlockData]) -> "NotionBlockList":
        instance = cls()
        for block_id, data in api_response.items():
            instance.append(NotionBlock(id=block_id, data=data))

        return instance

    def get_underlying_block_ids(self) -> set[BlockId]:
        block_ids: set[BlockId] = set(self.first_page_block.content) if self.first_page_block else set()

        for block in self.blocks_with_underliying_blocks():
            for block_id in block.content:
                if not self.have_block_with_id(block_id):
                    block_ids.add(block_id)

        return block_ids

    def get_block(self, block_id: BlockId) -> NotionBlock:
        for block in self.data:
            if block.id == block_id:
                return block

        raise KeyError("Block with id %s not found", block_id)

    def have_block_with_id(self, block_id: BlockId) -> bool:
        try:
            return self.get_block(block_id) is not None
        except KeyError:
            return False

    def blocks_with_underliying_blocks(self) -> Generator[NotionBlock, None, None]:
        """List of non-page blocks that have other blocks in it"""
        for block in self.data:
            if block.type != "page":
                if len(block.content) > 1:
                    yield block

    @property
    def first_page_block(self) -> NotionBlock | None:
        """We assume that first block with type == 'page' is the root block, that has some unlderlying blocks we should fetch"""
        for block in self.data:
            if block.type == "page" and len(block.content) > 0:
                return block
