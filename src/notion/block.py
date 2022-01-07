from typing import Optional

import contextlib
from collections import UserList
from dataclasses import dataclass

from notion.types import BlockId


@dataclass
class NotionBlock:
    id: BlockId
    data: dict

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
    def get_underlying_block_ids(self) -> set[BlockId]:
        block_ids: set[BlockId] = set()

        for block in self.data:
            for block_id in block.content:
                if not self.have_block_with_id(block_id):
                    block_ids.add(block_id)

        return block_ids

    def have_block_with_id(self, block_id: BlockId) -> bool:
        return len([block for block in self.data if block.id == block_id]) > 0
