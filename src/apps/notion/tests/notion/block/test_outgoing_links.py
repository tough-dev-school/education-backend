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
    blockdata["value"]["properties"]["title"] = [[[["h", "default"]]], ["| "], ["Урок 3 →", [["a", "/17705e42624c811f9ddsd8c32em54f0a"]]]]

    assert block(data=blockdata).get_outgoing_links() == ["17705e42624c811f9ddsd8c32em54f0a"]


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("/1b2a8e5f6c9d3b74e2f0a1c5d8e693f7#f8b7c6a1d5e0f2a3b4c9e1d7a5b6c382", "1b2a8e5f6c9d3b74e2f0a1c5d8e693f7"),
        ("/1b2a8e5f6c9d3b74e2f0a1c5d8e693f7?test=X", "1b2a8e5f6c9d3b74e2f0a1c5d8e693f7"),
        ("/1b2a8e5f6c9d3b74e2f0a1c5d8e693f7?test=X#combo", "1b2a8e5f6c9d3b74e2f0a1c5d8e693f7"),
    ],
)
def test_stripping(blockdata, raw, expected):
    blockdata["value"]["properties"]["title"] = [[[["h", "default"]]], ["| "], ["Урок 3 →", [["a", raw]]]]
    assert block(data=blockdata).get_outgoing_links() == [expected]


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
