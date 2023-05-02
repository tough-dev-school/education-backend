import pytest

from pytest_httpx import HTTPXMock


@pytest.fixture
def _ok(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="http://notion.middleware/v1/notion/syncRecordValues/",
        json={
            "recordMap": {
                "block": {
                    "first-block": {},
                    "second-block": {},
                },
            },
        },
    )


@pytest.mark.usefixtures("_ok")
def test_ok(notion):
    got = notion.fetch_blocks(["first-block", "second-block"])

    assert len(got) == 2
    assert got[0].id == "first-block"
    assert got[1].id == "second-block"
