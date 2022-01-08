from typing import Optional

from dataclasses import dataclass

from notion.block import NotionBlockList


@dataclass
class NotionPage:
    blocks: NotionBlockList
    comments: Optional[NotionBlockList] = NotionBlockList()
    discussions: Optional[NotionBlockList] = NotionBlockList()

    @classmethod
    def from_api_response(cls, api_response: dict) -> 'NotionPage':
        return cls(
            blocks=NotionBlockList.from_api_response(api_response['recordMap']['block']),
            comments=NotionBlockList.from_api_response(api_response['recordMap']['comment']),
            discussions=NotionBlockList.from_api_response(api_response['recordMap']['discussion']),
        )
