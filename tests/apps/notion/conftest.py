import pytest

from apps.notion.block import NotionBlock, NotionBlockList
from apps.notion.client import NotionClient
from apps.notion.page import NotionPage
from apps.notion.rewrite import fetched_assets, notion_so_assets

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def _cdn_dev_storage(settings):
    settings.STORAGES = {
        "default": {
            "BACKEND": "core.storages.ProdReadOnlyStorage",
        },
    }
    settings.AWS_S3_CUSTOM_DOMAIN = "cdn.tough-dev.school"


@pytest.fixture(autouse=True)
def _isolate_mapping_cache():
    """Asset links mappings are LRU-cached, so we need to reset it before year test run"""
    notion_so_assets.get_already_fetched_assets.cache_clear()
    fetched_assets.get_asset_mapping.cache_clear()

    yield
    notion_so_assets.get_already_fetched_assets.cache_clear()
    fetched_assets.get_asset_mapping.cache_clear()


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
                NotionBlock(
                    id="block-1",
                    data={
                        "role": "reader-1",
                        "value": {  # type: ignore
                            "id": "block-1",
                            "parent_table": "test",
                            "parent_id": "100500",
                            "_key_to_drop": "value_to_drop",
                        },
                    },
                ),
                NotionBlock(id="block-2", data={"value": {"parent_id": "100600"}}),
                NotionBlock(
                    id="block-3",
                    data={
                        "value": {
                            "id": "block-3",
                            "type": "page",
                            "content": ["block-1", "block-2"],
                            "format": {
                                "page_cover": "secure.notion-static.com/typicalmacuser.jpg",
                            },
                            "parent_table": "test-parent-table",
                        }
                    },
                ),
            ]
        )
    )


@pytest.fixture
def material(mixer, course):
    return mixer.blend(
        "notion.Material",
        course=course,
        page_id="0e5693d2173a4f77ae8106813b6e5329",
        slug="4d5726e8ee524448b8f97be4c7f8e632",
    )
