import pytest
from respx import MockRouter

from core.test.api_client import DRFClient


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
                    "third-block": {},
                    "fourth-block": {},
                },
            },
        },
    )


@pytest.fixture(autouse=True)
def mock_blocks_fetching(mocker):
    return mocker.patch("apps.notion.block.NotionBlockList.get_underlying_block_ids", return_value=[])
