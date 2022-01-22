from typing import Any, Generator, Optional

import contextlib
import pytz
from collections import UserList
from dataclasses import dataclass
from datetime import datetime

from notion.types import BlockId


@dataclass
class NotionBlock:
    id: BlockId
    data: dict[str, Any]

    @property
    def content(self) -> list[BlockId]:
        try:
            return self.data['value']['content']
        except KeyError:
            return list()

    @property
    def type(self) -> Optional[str]:
        with contextlib.suppress(KeyError):
            return self.data['value']['type']

    @property
    def last_modified(self) -> Optional[datetime]:
        with contextlib.suppress(KeyError):
            last_modified = datetime.fromtimestamp(int(self.data['value']['last_edited_time']) / 1000)
            return last_modified.replace(tzinfo=pytz.UTC)


class NotionBlockList(UserList[NotionBlock]):
    @classmethod
    def from_api_response(cls, api_response: dict[str, dict]) -> 'NotionBlockList':
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

    def have_block_with_id(self, block_id: BlockId) -> bool:
        return len([block for block in self.data if block.id == block_id]) > 0

    def blocks_with_underliying_blocks(self) -> Generator[NotionBlock, None, None]:
        """List of non-page blocks that have other blocks in it"""
        for block in self.data:
            if block.type != 'page':
                if len(block.content) > 1:
                    yield block

    @property
    def first_page_block(self) -> Optional[NotionBlock]:
        """We assume that first block with type == 'page' is the root block, that has some unlderlying blocks we should fetch"""
        for block in self.data:
            if block.type == 'page' and len(block.content) > 0:
                return block

    @property
    def last_modified(self) -> Optional[datetime]:
        blocks_with_last_modified = [block for block in self.data if block.last_modified is not None]

        if len(blocks_with_last_modified) == 0:
            return None

        latest_block = max(blocks_with_last_modified, key=lambda block: block.last_modified)  # type: ignore
        if latest_block is not None:
            return latest_block.last_modified
