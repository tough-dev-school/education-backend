import pytest

from apps.notion.block import NotionBlock


@pytest.fixture
def block_without_content() -> NotionBlock:
    return NotionBlock(id="without_content", data={})


@pytest.fixture
def block_with_content() -> NotionBlock:
    return NotionBlock(
        id="with_content",
        data={
            "value": {
                "content": ["a", "b", "c"],
                "last_edited_time": 1642356661000,
            },
        },
    )


@pytest.fixture
def another_block_with_content() -> NotionBlock:
    return NotionBlock(
        id="another_with_content",
        data={
            "value": {
                "content": ["c", "e", "f"],
                "last_edited_time": 1642356662000,
            },
        },
    )


@pytest.fixture
def page_block() -> NotionBlock:
    return NotionBlock(
        id="empty_page_block",
        data={
            "value": {
                "type": "page",
                "content": ["g", "h", "i"],
            },
        },
    )
