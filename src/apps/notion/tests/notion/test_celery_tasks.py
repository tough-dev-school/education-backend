import pytest

from apps.notion.tasks import update_cache, update_cache_for_all_pages
from apps.notion.models import NotionCacheEntryStatus
from apps.notion.exceptions import HTTPError
import contextlib

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def fetch_page(mocker, page):
    return mocker.patch(
        "apps.notion.client.NotionClient.fetch_page",
        return_value=page,
    )


@pytest.fixture(autouse=True)
def cache_set(mocker):
    return mocker.patch("apps.notion.cache.NotionCache.set")


def test_update_cache(fetch_page, cache_set, material, page):
    update_cache(material.page_id)

    cache_set.assert_called_once_with(material.page_id, page)
    fetch_page.assert_called_once_with(material.page_id)


def test_update_cache_sets_status(material):
    update_cache(material.page_id)

    status = NotionCacheEntryStatus.objects.get(page_id=material.page_id)

    assert status.fetch_started is not None
    assert status.fetch_complete is not None


def test_incomplete_fetch(material, fetch_page):
    """Make fetch fail and check if complete time is not updated"""
    fetch_page.side_effect = HTTPError()

    with contextlib.suppress(HTTPError):
        update_cache(material.page_id)

    status = NotionCacheEntryStatus.objects.get(page_id=material.page_id)

    assert status.fetch_started is not None
    assert status.fetch_complete is None


def test_update_cache_for_all_pages(fetch_page, cache_set, material, page, mixer):
    for _ in range(3):
        mixer.blend("notion.Material", active=False)
        mixer.blend("notion.Material", active=True, page_id=material.page_id)

    update_cache_for_all_pages()

    cache_set.assert_called_once_with(material.page_id, page)
    fetch_page.assert_called_once_with(material.page_id)
