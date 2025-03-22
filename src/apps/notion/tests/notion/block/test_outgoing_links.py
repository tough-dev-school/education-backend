import pytest

from apps.notion.block import NotionBlock


@pytest.fixture
def blockdata():
    return {
        "value": {
            "id": "test-block",
            "type": "text",
            "properties": {"title": []},
        },
    }


def block(**kwargs) -> NotionBlock:
    return NotionBlock(id="test-block", **kwargs)


def test_no_links(blockdata):
    assert block(data=blockdata).get_outgoing_links() == []


def test_non_text_block(blockdata):
    blockdata["value"]["type"] = "page"
    assert block(data=blockdata).get_outgoing_links() == []


def test_empty_text_block(blockdata):
    blockdata["value"] = {}
    assert block(data=blockdata).get_outgoing_links() == []


def test_link_inside_the_text(blockdata):
    blockdata["value"]["properties"]["title"] = [[[["h", "default"]]], ["| "], ["Урок 3 →", [["a", "/17705e42624c811f9ddsd8c32em54f0a?pvs=25"]]]]

    assert block(data=blockdata).get_outgoing_links() == ["17705e42624c811f9ddsd8c32em54f0a"]


def test_two_links_inside_the_text(blockdata):
    blockdata["value"]["properties"]["title"] = [
        [
            "← Урок 1",
            [
                [
                    "a",
                    "/c1a07d6928b87fc4a2e1b3fba4c8d1fe?pvs=25",
                ]
            ],
        ],
        [" ", [["h", "default"]]],
        ["| "],
        [
            "Урок 3 →",
            [
                [
                    "a",
                    "/b501d0c3465e28f9c7b3f8a51d72e3c4",
                ]
            ],
        ],
    ]

    assert block(data=blockdata).get_outgoing_links() == ["c1a07d6928b87fc4a2e1b3fba4c8d1fe", "b501d0c3465e28f9c7b3f8a51d72e3c4"]


def test_links_are_unique(blockdata):
    blockdata["value"]["properties"]["title"] = [
        [
            "← Урок 1",
            [
                [
                    "a",
                    "/c1a07d6928b87fc4a2e1b3fba4c8d1fe?pvs=25",
                ]
            ],
        ],
        [" ", [["h", "default"]]],
        ["| "],
        [
            "Урок 3 →",
            [
                [
                    "a",
                    "/c1a07d6928b87fc4a2e1b3fba4c8d1fe",
                ]
            ],
        ],
    ]
    assert block(data=blockdata).get_outgoing_links() == ["c1a07d6928b87fc4a2e1b3fba4c8d1fe"]


def test_external_links_are_ignored(blockdata):
    blockdata["value"]["properties"]["title"] = [[[["h", "default"]]], ["| "], ["Урок 3 →", [["a", "https://en.wikipedia.org/wiki/Test"]]]]

    assert block(data=blockdata).get_outgoing_links() == []
