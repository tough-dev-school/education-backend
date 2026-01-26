import pytest

from apps.notion.cache import NotionCache, get_cached_page_or_fetch
from apps.notion.models import NotionCacheEntry

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def cache_entry(page, mixer):
    return mixer.blend(
        "notion.NotionCacheEntry",
        page_id=page.id,
        content=page.to_json(),
    )


@pytest.fixture
def cache_set(mocker):
    return mocker.patch("apps.notion.cache.NotionCache.set")


@pytest.fixture
def fetch_page(mocker):
    return mocker.patch("apps.notion.client.NotionClient.fetch_page")


@pytest.fixture
def cache():
    return NotionCache()


@pytest.fixture
def page_from_callable(page, mocker):
    return mocker.MagicMock(return_value=page)


def test_set(cache, page):
    cache.set("some_key", page)

    cache_entry = NotionCacheEntry.objects.get()
    assert cache_entry.content == page.to_json()


def test_set_callable(cache, page_from_callable, page):
    cache.set("some_key", page_from_callable)

    cache_entry = NotionCacheEntry.objects.get()
    assert cache_entry.content == page.to_json()
    page_from_callable.assert_called_once()


def test_get(cache, page, cache_entry):
    got = cache.get(cache_entry.page_id)

    assert got == page


def test_set_and_get(cache, page):
    cache.set(page.id, page)

    got = cache.get(page.id)

    assert got == page


def test_get_cached_page_or_fetch_returns_cached_page(cache_entry, cache_set, fetch_page):
    get_cached_page_or_fetch(cache_entry.page_id)

    cache_set.assert_not_called()
    fetch_page.assert_not_called()
