from dataclasses import dataclass

from notion.block import NotionBlockList


@dataclass
class NotionPage:
    id: str
    blocks: NotionBlockList
    comments: NotionBlockList
    discussions: NotionBlockList

    @classmethod
    def from_api_response(cls, api_response: dict) -> 'NotionPage':
        return cls(
            id=api_response['cursor']['stack'][0][0]['id'],
            blocks=NotionBlockList.from_api_response(api_response['recordMap']['block']),
            comments=NotionBlockList.from_api_response(api_response['recordMap']['comment']),
            discussions=NotionBlockList.from_api_response(api_response['recordMap']['discussion']),
        )
