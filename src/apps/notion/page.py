import contextlib
from dataclasses import dataclass

from apps.notion import tasks
from apps.notion.block import NotionBlock, NotionBlockList
from apps.notion.exceptions import NotionResponseError, NotSharedForWeb
from apps.notion.types import NotionId


@dataclass
class NotionPage:
    """Has two entrypoints:
        1. NotionPage.from_api_response()
        2. NotionPage.from_json()
    The former bypasses some notion API quircks, the latter is intended to build page objects from cache, stored with .to_json() method

    NotionPage and NotionBlock stay isolated from django ORM. The only possible interacation is allowed via celery tasks.
    """

    id: NotionId
    blocks: NotionBlockList

    def to_json(self) -> dict:
        return {"blocks": [block.to_json() for block in self.blocks]}

    @classmethod
    def from_json(cls, data: dict, kwargs: dict[str, str | NotionId] | None = None) -> "NotionPage":
        kwargs = kwargs if kwargs is not None else dict()
        blocks = NotionBlockList([NotionBlock.from_json(block_dict) for block_dict in data["blocks"]])
        return cls(blocks=blocks, **kwargs)

    @classmethod
    def from_api_response(cls, response: dict, kwargs: dict[str, str | NotionId] | None = None) -> "NotionPage":
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
        """Called externaly after page fetching or updating"""
        self.save_assets()
        self.save_relations()

    def save_assets(self) -> None:
        """Save images and files from all underlying blocks"""
        for block in self.blocks:
            block.save_assets()

    def save_relations(self) -> None:
        """Save page outgoing links.

        Uses celery task to stay isolated from the ORM
        """
        links = list()
        for block in self.blocks:
            links += block.get_outgoing_links()

        if len(links):
            tasks.save_page_relations.delay(page_id=self.id, links=links)
