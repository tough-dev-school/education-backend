import pytest
from respx import MockRouter

from apps.notion.models import NotionCacheEntry, NotionCacheEntryStatus

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.repeat(3),
]


def test_request_is_done_for_the_first_time(api, respx_mock: MockRouter):
    api.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/")

    assert len(respx_mock.calls) == 1


def test_cache_entry_status_is_updated(api):
    api.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/")

    status = NotionCacheEntryStatus.objects.get(page_id="0e5693d2173a4f77ae8106813b6e5329")
    assert status.fetch_started is not None
    assert status.fetch_complete is not None


def test_request_is_cached(api, respx_mock: MockRouter):
    api.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/")
    api.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/")

    assert len(respx_mock.calls) == 1


def test_request_is_cached_in_notion_cache_model(api, respx_mock: MockRouter):
    api.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/")
    NotionCacheEntry.objects.all().delete()
    api.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/")

    assert len(respx_mock.calls) == 2


def test_staff_request_returns_uncached_page(api, as_staff, respx_mock: MockRouter):
    api.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/")
    as_staff.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/")

    assert len(respx_mock.calls) == 2


def test_staff_request_returns_cached_page_if_feature_flag_is_on(api, as_staff, respx_mock: MockRouter):
    api.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/")
    as_staff.get(
        "/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/",
        headers={
            "X-New-Material-Cache-Behaviour": True,
        },
    )
    assert len(respx_mock.calls) == 1


def test_staff_request_with_the_new_feature_flag_does_not_break_things(as_staff, respx_mock: MockRouter):
    as_staff.get(
        "/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/",
        headers={
            "X-New-Material-Cache-Behaviour": True,
        },
    )
    assert len(respx_mock.calls) == 1


def test_staff_request_sets_cache(api, as_staff, respx_mock: MockRouter):
    api.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/")
    as_staff.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/")
    api.get("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/")  # should not be called

    assert len(respx_mock.calls) == 2
