import pytest

from apps.notion.tasks import update_cache, update_cache_for_all_pages

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def mock_fetch_page_recursively(mocker, page):
    return mocker.patch(
        "apps.notion.client.NotionClient.fetch_page_recursively",
        return_value=page,
    )


@pytest.fixture
def mock_cache_set(mocker):
    return mocker.patch("apps.notion.cache.NotionCache.set")


def test_call_update_cache(mock_fetch_page_recursively, mock_cache_set, material, page):
    update_cache(material.page_id)

    mock_cache_set.assert_called_once_with(material.page_id, page)
    mock_fetch_page_recursively.assert_called_once_with(material.page_id)


def test_call_update_cache_for_all_pages(mock_fetch_page_recursively, mock_cache_set, material, page, mixer):
    for _ in range(3):
        mixer.blend("notion.Material", active=False)
        mixer.blend("notion.Material", active=True, page_id=material.page_id)

    update_cache_for_all_pages()

    mock_cache_set.assert_called_once_with(material.page_id, page)
    mock_fetch_page_recursively.assert_called_once_with(material.page_id)
