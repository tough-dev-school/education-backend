import pytest

from apps.notion.models import NotionCacheEntryStatus

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def status(material):
    return NotionCacheEntryStatus.objects.create(
        page_id=material.page_id,
        fetch_started="2032-12-01 15:30:00+03:00",
        fetch_complete="2032-12-01 15:30:05+03:00",
    )


@pytest.fixture
def api(api):
    api.user.update(is_staff=True)

    return api


def test(api, material):
    got = api.get(f"/api/v2/materials/{material.page_id}/status/")

    assert got["fetch_started"] == "2032-12-01T15:30:00+03:00"
    assert got["fetch_complete"] == "2032-12-01T15:30:05+03:00"


def test_admin_only(api, material):
    api.user.update(is_staff=False)

    api.get(f"/api/v2/materials/{material.page_id}/status/", expected_status_code=403)
