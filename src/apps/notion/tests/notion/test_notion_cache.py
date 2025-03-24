from datetime import timedelta

import pytest
from django.utils import timezone

from apps.notion.block import NotionBlock, NotionBlockList
from apps.notion.cache import TIMEOUT, NotionCache, get_cached_page_or_fetch
from apps.notion.models import NotionCacheEntry
from apps.notion.page import NotionPage

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def cache_entry(not_expired_datetime, page, mixer):
    return mixer.blend(
        "notion.NotionCacheEntry",
        page_id=page.id,
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
    return mocker.patch("apps.notion.client.NotionClient.fetch_page")


@pytest.fixture
def cache():
    return NotionCache()


@pytest.fixture
def another_page() -> NotionPage:
    return NotionPage(
        id="another-test-id",
        blocks=NotionBlockList(
            [
                NotionBlock(id="block-2", data={"role": "reader-6"}),
            ]
        ),
    )


@pytest.fixture
def page_from_callable(page, mocker):
    return mocker.MagicMock(return_value=page)


@pytest.fixture
def not_expired_datetime():
    return timezone.now() + timedelta(seconds=TIMEOUT)


@pytest.fixture
def expired_cache_entry(cache_entry):
    return cache_entry.update(expires=timezone.now() - timedelta(seconds=1))


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


def test_get_nothing_if_cache_expired(cache, expired_cache_entry):
    got = cache.get(expired_cache_entry.page_id)

    assert not got


def test_set_and_get(cache, page):
    cache.set(page.id, page)

    got = cache.get(page.id)

    assert got == page


def test_get_or_set_get_if_exists_and_not_expired(cache, page, cache_entry, page_from_callable):
    got = cache.get_or_set(cache_entry.page_id, content=page_from_callable)

    page_from_callable.assert_not_called()

    assert got == page
    assert got != page_from_callable


def test_get_or_set_set_if_expired(cache, another_page, expired_cache_entry):
    got = cache.get_or_set(expired_cache_entry.page_id, content=another_page)

    newly_created_cache_entry = NotionCacheEntry.objects.get(page_id=expired_cache_entry.page_id)

    assert got == another_page
    assert got == NotionPage.from_json(newly_created_cache_entry.content, kwargs={"id": another_page.id})


def test_get_or_set_set_if_doesnt_exist(cache, another_page):
    got = cache.get_or_set(another_page.id, content=another_page)

    newly_created_cache_entry = NotionCacheEntry.objects.get(page_id=another_page.id)

    assert got == another_page
    assert got == NotionPage.from_json(newly_created_cache_entry.content, kwargs={"id": another_page.id})


@pytest.mark.parametrize("env_value", ["On", ""])
@pytest.mark.usefixtures("current_user_casual")
def test_user_always_gets_page_from_existing_cache(settings, cache_entry, env_value, cache_set, fetch_page):
    settings.NOTION_CACHE_ONLY = bool(env_value)

    get_cached_page_or_fetch(cache_entry.page_id)

    cache_set.assert_not_called()
    fetch_page.assert_not_called()


@pytest.mark.usefixtures("current_user_staff")
def test_staff_user_get_page_from_cache_if_cache_only_mode_is_enabled(settings, cache_entry, cache_set, fetch_page):
    settings.NOTION_CACHE_ONLY = bool("On")

    get_cached_page_or_fetch(cache_entry.page_id)

    cache_set.assert_not_called()
    fetch_page.assert_not_called()


@pytest.mark.usefixtures("current_user_staff")
def test_staff_user_get_page_from_notion_if_cache_only_mode_is_disabled(settings, cache_entry, cache_set, fetch_page):
    settings.NOTION_CACHE_ONLY = bool("")

    got = get_cached_page_or_fetch(cache_entry.page_id)

    page = fetch_page.return_value
    assert got == page
    cache_set.assert_called_once_with(cache_entry.page_id, page)
    fetch_page.assert_called_once_with(cache_entry.page_id)
