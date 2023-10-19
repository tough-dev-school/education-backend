import pytest

from apps.notion.block import NotionBlock
from apps.notion.block import NotionBlockList
from apps.notion.client import NotionClient
from apps.notion.page import NotionPage

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def staff_user(mixer):
    user = mixer.blend("users.User", is_superuser=False, is_staff=True)
    user.add_perm("notion.material.see_all_materials")

    return user


@pytest.fixture
def notion() -> NotionClient:
    return NotionClient()


@pytest.fixture(autouse=True)
def _freeze_notion_middleware_url(settings):
    settings.NOTION_MIDDLEWARE_URL = "http://notion.middleware"


@pytest.fixture
def fetch_blocks(mocker):
    return mocker.patch("apps.notion.client.NotionClient.fetch_blocks")


@pytest.fixture
def fetch_page(mocker):
    return mocker.patch("apps.notion.client.NotionClient.fetch_page")


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


@pytest.fixture
def page_as_dict(page):
    first_block = page.blocks[0]
    second_block = page.blocks[1]
    return {
        "blocks": [
            {
                "id": first_block.id,
                "data": first_block.data,
            },
            {
                "id": second_block.id,
                "data": second_block.data,
            },
        ]
    }


@pytest.fixture
def cache_entry(not_expired_datetime, page_as_dict, mixer):
    return mixer.blend(
        "notion.NotionCacheEntry",
        cache_key="some_key",
        content=page_as_dict,
        expires=not_expired_datetime,
    )


@pytest.fixture
def material(mixer, course):
    return mixer.blend(
        "notion.Material",
        course=course,
        page_id="0e5693d2173a4f77ae8106813b6e5329",
        slug="4d5726e8ee524448b8f97be4c7f8e632",
    )
