import pytest

from pytest_httpx import HTTPXMock


@pytest.fixture
def _ok(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://www.notion.so/api/v3/syncRecordValues",
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
