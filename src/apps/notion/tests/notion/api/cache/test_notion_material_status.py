import pytest

from apps.notion.models import NotionCacheEntryStatus

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("material"),
]


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


@pytest.mark.parametrize("page_id", ["0e5693d2-173a-4f77-ae81-06813b6e5329", "0e5693d2173a4f77ae8106813b6e5329"])
def test_by_page_id(api, page_id):
    got = api.get(f"/api/v2/materials/{page_id}/status/")

    assert got["fetch_started"] == "2032-12-01T15:30:00+03:00"
    assert got["fetch_complete"] == "2032-12-01T15:30:05+03:00"


@pytest.mark.parametrize("material_slug", ["4d5726e8-ee52-4448-b8f9-7be4c7f8e632", "4d5726e8ee524448b8f97be4c7f8e632"])
def test_by_slug(api, material_slug):
    got = api.get(f"/api/v2/materials/{material_slug}/status/")

    assert got["fetch_started"] == "2032-12-01T15:30:00+03:00"
    assert got["fetch_complete"] == "2032-12-01T15:30:05+03:00"


def test_admin_only(api, material):
    api.user.update(is_staff=False)

    api.get(f"/api/v2/materials/{material.page_id}/status/", expected_status_code=403)
