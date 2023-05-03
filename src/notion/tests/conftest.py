import pytest

from notion.client import NotionClient


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
