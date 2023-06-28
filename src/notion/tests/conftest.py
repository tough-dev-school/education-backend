import pytest

from notion.block import NotionBlock
from notion.block import NotionBlockList
from notion.client import NotionClient
from notion.page import NotionPage


@pytest.fixture
def notion() -> NotionClient:
    return NotionClient()


@pytest.fixture(autouse=True)
def _freeze_notion_middleware_url(settings):
    settings.NOTION_MIDDLEWARE_URL = "http://notion.middleware"


@pytest.fixture
def fetch_blocks(mocker):
    return mocker.patch("notion.client.NotionClient.fetch_blocks")


@pytest.fixture
def fetch_page(mocker):
    return mocker.patch("notion.client.NotionClient.fetch_page")


@pytest.fixture
def page() -> NotionPage:
    return NotionPage(
        blocks=NotionBlockList(
            [
                NotionBlock(id="block-1", data={"role": "reader-1", "value": {"last_edited_time": 1642356660000}}),
                NotionBlock(id="block-2", data={"role": "reader-2"}),
            ]
        )
    )
