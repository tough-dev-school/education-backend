import pytest

from apps.notion.models import NotionCacheEntryStatus

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def api(api):
    api.user.update(is_staff=True)

    return api


@pytest.mark.parametrize("page_id", ["0e5693d2-173a-4f77-ae81-06813b6e5329", "0e5693d2173a4f77ae8106813b6e5329"])
def test_update_by_page_id(api, page_id, respx_mock):
    api.put(f"/api/v2/materials/{page_id}/update/")

    assert len(respx_mock.calls) == 1


@pytest.mark.parametrize("material_slug", ["4d5726e8-ee52-4448-b8f9-7be4c7f8e632", "4d5726e8ee524448b8f97be4c7f8e632"])
def test_update_by_slug(api, material_slug, respx_mock):
    api.put(f"/api/v2/materials/{material_slug}/update/")

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
