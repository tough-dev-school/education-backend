import pytest

from notion.client import NotionClient


@pytest.fixture
def notion() -> NotionClient:
    return NotionClient()


@pytest.fixture(autouse=True)
def _configure_notion_settings(settings):
    settings.NOTION_TOKEN = "tsttkn"


@pytest.fixture
def fetch_blocks(mocker):
    return mocker.patch("notion.client.NotionClient.fetch_blocks")


@pytest.fixture
def fetch_page(mocker):
    return mocker.patch("notion.client.NotionClient.fetch_page")
