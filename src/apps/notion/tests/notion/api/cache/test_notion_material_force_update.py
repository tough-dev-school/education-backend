import pytest

from apps.notion.models import NotionCacheEntryStatus

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def api(api):
    api.user.update(is_staff=True)

    return api


def test_update(api, respx_mock):
    api.put("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/update/")

    assert len(respx_mock.calls) == 1


def test_admin_only(api):
    api.user.update(is_staff=False)

    api.put("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/update/", expected_status_code=403)


@pytest.mark.skip("Not implemented")
def test_peding_update_blocks_one_more_update(api, respx_mock):
    NotionCacheEntryStatus.objects.create(
        page_id="0e5693d2173a4f77ae8106813b6e5329",
        fetch_started="2032-12-01 15:30:00+03:00",
        fetch_complete=None,
    )

    api.put("/api/v2/materials/0e5693d2173a4f77ae8106813b6e5329/update/", expected_status_code=400)
    assert len(respx_mock.calls) == 0
