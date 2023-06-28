import pytest

from notion.tasks import update_cache_for_all_active_notion_materials
from notion.tasks import update_cache_notion_material

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def mock_fetch_page_recursively(mocker, page):
    return mocker.patch(
        "notion.client.NotionClient.fetch_page_recursively",
        return_value=page,
    )


@pytest.fixture
def mock_cache_set(mocker):
    return mocker.patch("notion.cache.NotionCache.set")


def test_call_update_cache_notion_material(mock_fetch_page_recursively, mock_cache_set, material, page):
    update_cache_notion_material(material.page_id)

    mock_cache_set.assert_called_once_with(material.page_id, page)
    mock_fetch_page_recursively.assert_called_once_with(material.page_id)


def test_call_update_cache_for_all_active_notion_materials(mock_fetch_page_recursively, mock_cache_set, material, page, mixer):
    for _ in range(3):
        mixer.blend("notion.Material", active=False)
        mixer.blend("notion.Material", active=True, page_id=material.page_id)

    update_cache_for_all_active_notion_materials()

    mock_cache_set.assert_called_once_with(material.page_id, page)
    mock_fetch_page_recursively.assert_called_once_with(material.page_id)
