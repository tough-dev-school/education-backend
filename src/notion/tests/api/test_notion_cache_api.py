import pytest

from respx import MockRouter

from app.test.api_client import DRFClient
from notion.models import NotionCacheEntry

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.repeat(3),
]


@pytest.fixture
def as_staff(staff_user):
    return DRFClient(user=staff_user)


@pytest.fixture(autouse=True)
def _ok(respx_mock: MockRouter):
    respx_mock.route(url="http://notion.middleware/v1/notion/loadPageChunk/").respond(
        json={
            "recordMap": {
                "__version__": 3,
                "block": {
                    "first-block": {
                        "role": "editor",
                        "value": {
                            "id": "first-block",
                            "type": "page",
                            "properties": {
                                "title": [["Неделя 1 из 4"]],
                            },
                            "content": [
                                "third-block",
                                "fourth-block",
                            ],
                        },
                    },
                    "second-block": {},
                },
            },
        },
    )


@pytest.fixture(autouse=True)
def mock_blocks_fetching(mocker):
    return mocker.patch("notion.block.NotionBlockList.get_underlying_block_ids", return_value=[])


def test_request_is_done_for_the_first_time(api, respx_mock: MockRouter):
    api.get("/api/v2/notion/materials/0e5693d2173a4f77ae8106813b6e5329/")

    assert len(respx_mock.calls) == 1


def test_request_is_cached(api, respx_mock: MockRouter):
    api.get("/api/v2/notion/materials/0e5693d2173a4f77ae8106813b6e5329/")
    api.get("/api/v2/notion/materials/0e5693d2173a4f77ae8106813b6e5329/")

    assert len(respx_mock.calls) == 1


def test_request_is_cached_in_notion_cache_model(api, respx_mock: MockRouter):
    api.get("/api/v2/notion/materials/0e5693d2173a4f77ae8106813b6e5329/")
    NotionCacheEntry.objects.all().delete()
    api.get("/api/v2/notion/materials/0e5693d2173a4f77ae8106813b6e5329/")

    assert len(respx_mock.calls) == 2


def test_staff_request_returns_uncached_page(api, as_staff, respx_mock: MockRouter):
    api.get("/api/v2/notion/materials/0e5693d2173a4f77ae8106813b6e5329/")
    as_staff.get("/api/v2/notion/materials/0e5693d2173a4f77ae8106813b6e5329/")

    assert len(respx_mock.calls) == 2


def test_staff_request_sets_cache(api, as_staff, respx_mock: MockRouter):
    api.get("/api/v2/notion/materials/0e5693d2173a4f77ae8106813b6e5329/")
    as_staff.get("/api/v2/notion/materials/0e5693d2173a4f77ae8106813b6e5329/")
    api.get("/api/v2/notion/materials/0e5693d2173a4f77ae8106813b6e5329/")  # should not be called

    assert len(respx_mock.calls) == 2
