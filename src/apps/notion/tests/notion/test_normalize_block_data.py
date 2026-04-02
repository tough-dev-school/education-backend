import pytest

from apps.notion.block import NotionBlockList, _normalize_block_data

OLD_FORMAT_BLOCK = {
    "role": "reader",
    "value": {"id": "block-1", "type": "text", "properties": {"title": [["hello"]]}},
}

NEW_FORMAT_BLOCK = {
    "value": {
        "role": "reader",
        "value": {"id": "block-1", "type": "text", "properties": {"title": [["hello"]]}},
    },
    "spaceId": "space-123",
}

NEW_FORMAT_BLOCK_NO_SPACE_ID = {
    "value": {
        "role": "reader",
        "value": {"id": "block-1", "type": "text", "properties": {"title": [["hello"]]}},
    },
}


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (OLD_FORMAT_BLOCK, OLD_FORMAT_BLOCK),
        (NEW_FORMAT_BLOCK, NEW_FORMAT_BLOCK["value"]),
        (NEW_FORMAT_BLOCK_NO_SPACE_ID, NEW_FORMAT_BLOCK_NO_SPACE_ID["value"]),
        ({}, {}),
    ],
    ids=["old-format", "new-format", "new-format-no-space-id", "empty-block"],
)
def test_normalize_block_data(data, expected):
    assert _normalize_block_data(data) == expected


def test_from_api_response_normalizes_new_format():
    api_response = {
        "block-1": NEW_FORMAT_BLOCK,
        "block-2": OLD_FORMAT_BLOCK,
    }

    blocks = NotionBlockList.from_api_response(api_response)

    assert blocks[0].data == NEW_FORMAT_BLOCK["value"]
    assert blocks[1].data == OLD_FORMAT_BLOCK


def test_block_properties_work_after_normalization():
    api_response = {
        "block-1": NEW_FORMAT_BLOCK,
    }

    blocks = NotionBlockList.from_api_response(api_response)
    block = blocks[0]

    assert block.type == "text"
    assert block.properties == {"title": "hello"}
    assert block.content == []
