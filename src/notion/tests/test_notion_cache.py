from datetime import timedelta
import pytest

from django.utils import timezone

from notion.block import NotionBlock
from notion.block import NotionBlockList
from notion.cache import NotionCache
from notion.models import NotionCacheEntry
from notion.page import NotionPage

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def cache():
    return NotionCache()


@pytest.fixture
def another_page() -> NotionPage:
    return NotionPage(
        blocks=NotionBlockList(
            [
                NotionBlock(id="block-1", data={"role": "reader-0", "value": {"last_edited_time": 1642356661234}}),
                NotionBlock(id="block-2", data={"role": "reader-6"}),
            ]
        )
    )


@pytest.fixture
def page_from_callable(page):
    def get_page():
        return page

    return get_page


@pytest.fixture
def not_expiring_datetime():
    return timezone.now() + timedelta(days=14)


@pytest.fixture
def expired_datetime():
    return timezone.now() - timedelta(seconds=7)


@pytest.fixture
def cache_entry(not_expiring_datetime, page, mixer):
    return mixer.blend(
        "notion.NotionCacheEntry",
        cache_key="some_key",
        content=page,
        expires=not_expiring_datetime,
    )


@pytest.fixture
def expired_cache_entry(cache_entry, expired_datetime):
    cache_entry.setattr_and_save("expires", expired_datetime)
    return cache_entry


def test_set(cache, page):
    cache.set("some_key", page)

    assert NotionCacheEntry.objects.count() == 1


def test_set_callable(cache, page, page_from_callable):
    cache.set("some_key", page_from_callable)

    cache_entry = NotionCacheEntry.objects.get()
    assert cache_entry.content == page


def test_get(cache, page, cache_entry):
    got = cache.get(cache_entry.cache_key)

    assert got == page
    assert got == cache_entry.content


def test_get_nothing_if_cache_expired(cache, expired_cache_entry):
    got = cache.get(expired_cache_entry.cache_key)

    assert not got


def test_get_deletes_expired_cache(cache, expired_cache_entry):
    cache.get(expired_cache_entry.cache_key)

    assert NotionCacheEntry.objects.count() == 0


def test_set_and_get(cache, page):
    cache.set("some_key", page)
    got = cache.get("some_key")

    assert got == page


def test_get_or_set_get_if_exists_and_not_expired(cache, another_page, cache_entry):
    got = cache.get_or_set(cache_entry.cache_key, content=another_page)

    assert got != another_page
    assert got == cache_entry.content


def test_get_or_set_set_if_expired(cache, another_page, expired_cache_entry):
    got = cache.get_or_set(expired_cache_entry.cache_key, content=another_page)

    new_cache_entry = NotionCacheEntry.objects.get(cache_key=expired_cache_entry.cache_key)
    assert got == another_page
    assert got == new_cache_entry.content


def test_get_or_set_set_if_doesnt_exist(cache, another_page):
    got = cache.get_or_set("some random cache key", content=another_page)

    new_cache_entry = NotionCacheEntry.objects.get(cache_key="some random cache key")
    assert got == another_page
    assert got == new_cache_entry.content
