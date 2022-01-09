from typing import Optional

import contextlib
from dataclasses import dataclass

from notion.block import NotionBlockList


@dataclass
class NotionPage:
    blocks: NotionBlockList

    @classmethod
    def from_api_response(cls, api_response: dict) -> 'NotionPage':
        return cls(
            blocks=NotionBlockList.from_api_response(api_response['recordMap']['block']),
        )

    @property
    def title(self) -> Optional[str]:
        if self.blocks.first_page_block is not None:
            with contextlib.suppress(KeyError, IndexError):
                return self.blocks.first_page_block.data['value']['properties']['title'][0][0]
