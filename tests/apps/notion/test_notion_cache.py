from datetime import timedelta

import pytest
from django.utils import timezone

from apps.notion.block import NotionBlock, NotionBlockList
from apps.notion.cache import TIMEOUT, NotionCache, get_cached_page
from apps.notion.models import NotionCacheEntry
from apps.notion.page import NotionPage

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def cache_entry(not_expired_datetime, page, mixer):
    return mixer.blend(
        "notion.NotionCacheEntry",
        cache_key="some_key",
        content=page.to_json(),
        expires=not_expired_datetime,
    )


@pytest.fixture
def current_user_staff(mocker, staff_user):
    return mocker.patch("apps.notion.cache.get_current_user", return_value=staff_user)


@pytest.fixture
def current_user_casual(mocker, user):
    return mocker.patch("apps.notion.cache.get_current_user", return_value=user)


@pytest.fixture
def cache_set(mocker):
    return mocker.patch("apps.notion.cache.NotionCache.set")


@pytest.fixture
def fetch_page(mocker):
    return mocker.patch("apps.notion.client.NotionClient.fetch_page_recursively")


@pytest.fixture
def cache():
    return NotionCache()


@pytest.fixture
def another_page() -> NotionPage:
    return NotionPage(
        blocks=NotionBlockList(
            [
                NotionBlock(id="block-2", data={"role": "reader-6"}),
            ]
        )
    )


@pytest.fixture
def page_from_callable(page, mocker):
    return mocker.MagicMock(return_value=page)


@pytest.fixture
def not_expired_datetime():
    return timezone.now() + timedelta(seconds=TIMEOUT)


@pytest.fixture
def expired_datetime():
    return timezone.now()


@pytest.fixture
def expired_cache_entry(cache_entry, expired_datetime):
    return cache_entry.update(expires=expired_datetime)


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
    got = cache.get(cache_entry.cache_key)

    assert got == page


def test_get_nothing_if_cache_expired(cache, expired_cache_entry):
    got = cache.get(expired_cache_entry.cache_key)

    assert not got


def test_set_and_get(cache, page):
    cache.set("some_key", page)

    got = cache.get("some_key")

    assert got == page


def test_get_or_set_get_if_exists_and_not_expired(cache, page, cache_entry, page_from_callable):
    got = cache.get_or_set(cache_entry.cache_key, content=page_from_callable)

    page_from_callable.assert_not_called()
    assert got == page
    assert got != page_from_callable


def test_get_or_set_set_if_expired(cache, another_page, expired_cache_entry):
    got = cache.get_or_set(expired_cache_entry.cache_key, content=another_page)

    new_cache_entry = NotionCacheEntry.objects.get(cache_key=expired_cache_entry.cache_key)
    assert got == another_page
    assert got == NotionPage.from_json(new_cache_entry.content)


def test_get_or_set_set_if_doesnt_exist(cache, another_page):
    got = cache.get_or_set("some random cache key", content=another_page)

    new_cache_entry = NotionCacheEntry.objects.get(cache_key="some random cache key")
    assert got == another_page
    assert got == NotionPage.from_json(new_cache_entry.content)


@pytest.mark.parametrize("env_value", ["On", ""])
@pytest.mark.usefixtures("current_user_casual")
def test_user_always_gets_page_from_existing_cache(settings, cache_entry, env_value, cache_set, fetch_page):
    settings.NOTION_CACHE_ONLY = bool(env_value)

    get_cached_page(cache_entry.cache_key)

    cache_set.assert_not_called()
    fetch_page.assert_not_called()


@pytest.mark.usefixtures("current_user_staff")
def test_staff_user_get_page_from_cache_if_cache_only_mode_is_enabled(settings, cache_entry, cache_set, fetch_page):
    settings.NOTION_CACHE_ONLY = bool("On")

    get_cached_page(cache_entry.cache_key)

    cache_set.assert_not_called()
    fetch_page.assert_not_called()


@pytest.mark.usefixtures("current_user_staff")
def test_staff_user_get_page_from_notion_if_cache_only_mode_is_disabled(settings, cache_entry, cache_set, fetch_page):
    settings.NOTION_CACHE_ONLY = bool("")

    got = get_cached_page(cache_entry.cache_key)

    page = fetch_page.return_value
    assert got == page
    cache_set.assert_called_once_with(cache_entry.cache_key, page)
    fetch_page.assert_called_once_with(cache_entry.cache_key)
