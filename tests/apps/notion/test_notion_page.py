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

@pytest.fixture
def set_response(respx_mock: MockRouter):
    def _set_response(response):
        respx_mock.route(url="http://notion.middleware/v1/notion/loadPageChunk/").respond(json=response)

    return _set_response

@pytest.fixture
def get_page(notion):
    return lambda: notion.fetch_page("0cb348b3a2d24c05bc944e2302fa553")

@pytest.fixture
def get_blocks(get_page):
    return lambda: get_page().blocks.ordered()

def test_ok(set_response, ok, get_blocks):
    set_response(ok)

    blocks = get_blocks()

    assert len(blocks) == 4
    assert blocks[0].id == "first-block"
    assert blocks[1].id == "second-block"
    assert blocks[2].id == "third-block"


def test_page_block_is_always_first(set_response, ok, get_blocks):
    ok["recordMap"]["block"]["first-block"]["value"]["type"] = "Bullshit"
    ok["recordMap"]["block"]["fourth-block"] = {
        "value": {
            "type": "page",
            "content": ["third-block", "second-block"],
        }
    }

    set_response(ok)

    blocks = get_blocks()

    assert blocks[0].id == "fourth-block"  # first block with type =="page"
    assert blocks[1].id == "first-block"
    assert blocks[2].id == "second-block"


def test_page_title(set_response, ok, get_page):
    set_response(ok)

    page = get_page()

    assert page.title == "Неделя 1 из 4"


def test_abscense_of_the_page_block_does_not_break_page_title(set_response, ok, get_page):
    set_response(ok)

    page = get_page()
    del page.blocks[0]

    assert page.title is None


def test_block_without_title_does_not_break_page_title_1(set_response, ok, get_page):
    set_response(ok)

    page = get_page()
    del page.blocks[0].data["value"]["properties"]["title"]

    assert page.title is None


def test_block_without_title_does_not_break_page_title_2(set_response, ok, get_page):
    set_response(ok)

    page = get_page()
    page.blocks[0].data["value"]["properties"]["title"] = []

    assert page.title is None


def test_not_shared_exception(get_page, set_response):
    set_response({
            "recordMap": {},  # not shared page looks excactly like this
        },
    )
    with pytest.raises(NotSharedForWeb):
        get_page()


def test_wrong_response_exception(get_page, set_response):
    set_response({"errorId": "de586d84-7fbb-466b-b633-8b1ae5cf0497", "name": "ValidationError", "message": "Invalid input."})

    with pytest.raises(NotionResponseError):
        get_page()
