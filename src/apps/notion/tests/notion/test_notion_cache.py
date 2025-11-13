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
