import pytest

from respx import MockRouter

from apps.notion.exceptions import NotionResponseError
from apps.notion.exceptions import NotSharedForWeb

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture()
def ok():
    return {
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
                            "second-block",
                            "third-block",
                            "fourth-block",
                        ],
                    },
                },
                "second-block": {},
                "third-block": {},
                "fourth-block": {},
            },
        },
    }


def test_ok(respx_mock: MockRouter, ok, notion):
    respx_mock.route(url="http://notion.middleware/v1/notion/loadPageChunk/").respond(json=ok)

    page = notion.fetch_page("0cb348b3a2d24c05bc944e2302fa553")
    blocks = page.blocks.ordered()

    assert len(blocks) == 4
    assert blocks[0].id == "first-block"
    assert blocks[1].id == "second-block"
    assert blocks[2].id == "third-block"


def test_blocks_are_ordered(respx_mock: MockRouter, ok, notion):
    """Change order in the first page block and make sure response is alligned with it"""
    ok["recordMap"]["block"]["first-block"]["value"]["content"] = [
        "fourth-block",
        "third-block",
        "second-block",
    ]
    respx_mock.route(url="http://notion.middleware/v1/notion/loadPageChunk/").respond(json=ok)

    page = notion.fetch_page("0cb348b3a2d24c05bc944e2302fa553")
    blocks = page.blocks.ordered()

    assert len(blocks) == 4
    assert blocks[0].id == "first-block"
    assert blocks[1].id == "fourth-block"
    assert blocks[2].id == "third-block"
    assert blocks[3].id == "second-block"


def test_page_block_is_always_first(respx_mock, ok, notion):
    ok["recordMap"]["block"]["first-block"]["value"]["type"] = "Bullshit"
    ok["recordMap"]["block"]["fourth-block"] = {
        "value": {
            "type": "page",
            "content": ["third-block", "second-block"],
        }
    }

    respx_mock.route(url="http://notion.middleware/v1/notion/loadPageChunk/").respond(json=ok)

    page = notion.fetch_page("0cb348b3a2d24c05bc944e2302fa553")
    blocks = page.blocks.ordered()

    assert blocks[0].id == "fourth-block"  # first block with type =="page"
    assert blocks[1].id == "third-block"
    assert blocks[2].id == "second-block"


def test_page_title(respx_mock: MockRouter, ok, notion):
    respx_mock.route(url="http://notion.middleware/v1/notion/loadPageChunk/").respond(json=ok)

    page = notion.fetch_page("0cb348b3a2d24c05bc944e2302fa553")

    assert page.title == "Неделя 1 из 4"


def test_abscense_of_the_page_block_does_not_break_page_title(respx_mock: MockRouter, ok, notion):
    respx_mock.route(url="http://notion.middleware/v1/notion/loadPageChunk/").respond(json=ok)

    page = notion.fetch_page("0cb348b3a2d24c05bc944e2302fa553")

    del page.blocks[0]

    assert page.title is None


def test_block_without_title_does_not_break_page_title_1(respx_mock: MockRouter, ok, notion):
    respx_mock.route(url="http://notion.middleware/v1/notion/loadPageChunk/").respond(json=ok)

    page = notion.fetch_page("0cb348b3a2d24c05bc944e2302fa553")

    del page.blocks[0].data["value"]["properties"]["title"]

    assert page.title is None


def test_block_without_title_does_not_break_page_title_2(respx_mock: MockRouter, ok, notion):
    respx_mock.route(url="http://notion.middleware/v1/notion/loadPageChunk/").respond(json=ok)

    page = notion.fetch_page("0cb348b3a2d24c05bc944e2302fa553")

    page.blocks[0].data["value"]["properties"]["title"] = []

    assert page.title is None


def test_not_shared_exception(notion, respx_mock: MockRouter):
    respx_mock.route(url="http://notion.middleware/v1/notion/loadPageChunk/").respond(
        json={
            "recordMap": {},  # not shared page looks excactly like this
        },
    )
    with pytest.raises(NotSharedForWeb):
        notion.fetch_page("0cb348b3a2d24c05bc944e2302fa553")


def test_wrong_response_exception(notion, respx_mock: MockRouter):
    respx_mock.route(url="http://notion.middleware/v1/notion/loadPageChunk/").respond(
        json={"errorId": "de586d84-7fbb-466b-b633-8b1ae5cf0497", "name": "ValidationError", "message": "Invalid input."},
    )
    with pytest.raises(NotionResponseError):
        notion.fetch_page("0cb348b3a2d24c05bc944e2302fa553")
