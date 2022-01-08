from typing import Any, Generator, Optional

import contextlib
from collections import UserList
from dataclasses import dataclass

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


class NotionBlockList(UserList[NotionBlock]):
    @classmethod
    def from_api_response(cls, api_response: dict[str, dict]) -> 'NotionBlockList':
        instance = cls()
        for block_id, data in api_response.items():
            instance.append(NotionBlock(id=block_id, data=data))

        return instance

    def get_underlying_block_ids(self) -> set[BlockId]:
        block_ids: set[BlockId] = set()

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
