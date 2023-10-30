import pytest

from apps.notion.block import NotionBlock


@pytest.mark.parametrize(
    ("block", "expected_type"),
    [
        ({}, None),
        ({"value": {"test": "zero"}}, None),
        ({"value": {"type": "testing"}}, "testing"),
    ],
)
def test_block_type(block, expected_type):
    assert NotionBlock(id="test", data=block).type == expected_type


@pytest.mark.parametrize(
    ("block", "expected_content"),
    [
        ({}, []),
        ({"value": {"test": "zero"}}, []),
        ({"value": {"content": ["a", "b"]}}, ["a", "b"]),
    ],
)
def test_content(block, expected_content):
    assert NotionBlock(id="test", data=block).content == expected_content
