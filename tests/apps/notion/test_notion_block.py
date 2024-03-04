import pytest

from apps.notion.block import NotionBlock


@pytest.mark.parametrize(
    ("block", "expected"),
    [
        ({}, None),
        ({"value": {"test": "zero"}}, None),
        ({"value": {"type": "testing"}}, "testing"),
    ],
)
def test_block_type(block, expected):
    assert NotionBlock(id="test", data=block).type == expected


@pytest.mark.parametrize(
    ("block", "expected"),
    [
        ({}, []),
        ({"value": {"test": "zero"}}, []),
        ({"value": {"content": ["a", "b"]}}, ["a", "b"]),
    ],
)
def test_content(block, expected):
    assert NotionBlock(id="test", data=block).content == expected


@pytest.mark.parametrize(
    ("block", "expected"),
    [
        ({}, {}),
        ({"value": {"no": "data"}}, {}),
        ({"value": {"properties": {
            "size": [["100x300"]],
            "source": [["https://typicalmacuser.jpg"]],
        }}}, {'size': "100x300", "source": "https://typicalmacuser.jpg"}),
    ]
)
def test_block_properties(block, expected):
    assert NotionBlock(id="test", data=block).properties == expected


@pytest.mark.parametrize(
    ("block", "expected"),
    [
        ({}, {}),
        ({"value": {"no": "data"}}, {}),
        ({"value": {"format": {
            "size": "100x300",
            "source": "https://typicalmacuser.jpg",
        }}}, {'size': "100x300", "source": "https://typicalmacuser.jpg"}),
    ]
)
def test_block_format(block, expected):
    assert NotionBlock(id="test", data=block).format == expected
