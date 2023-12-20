import pytest

from apps.notion.block import NotionBlock


@pytest.mark.parametrize(("block", "expected"), [
    ({}, []),
    ({"value": {"test": "zero"}}, []),
    ({"value": {
        "type": "page",
        "format": {"no": "test"},
    }}, []),
    ({"value": {
        "type": "page",
        "format": {
            "page_cover": "secure.notion-static.com/typicalmacuser.jpg",
            "page_icon": "secure.notion-static.com/typicalmacuser_icon.jpg",
        },
    }},
    [
        "secure.notion-static.com/typicalmacuser_icon.jpg",
        "secure.notion-static.com/typicalmacuser.jpg",
    ]),
    ({"value": {
        "type": "page",
        "format": {
            "page_cover": "secure.notion-static.com/typicalmacuser.jpg",
        },
    }},
    [
        "secure.notion-static.com/typicalmacuser.jpg",
    ]),
    ({"value": {
        "type": "page",
        "format": {
            "page_cover": "secure.notion-static.com/typicalmacuser.jpg",
            "page_icon": "💩",
        },
    }},
    [
        "secure.notion-static.com/typicalmacuser.jpg",
    ]),

])
def test_page(block, expected):
    assert NotionBlock(id="test-block", data=block).get_assets_to_save() == expected


def test_image():
    block = NotionBlock(id="test-block", data={
        "value": {
            "type": "image",
            "properties": {
                "source": [["secure.notion-static.com/typicalmacuser.jpg"]],
            },
        },
    })
    assert block.get_assets_to_save() == ["secure.notion-static.com/typicalmacuser.jpg"]
