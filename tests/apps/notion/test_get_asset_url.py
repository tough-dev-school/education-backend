from apps.notion.assets import get_asset_url
from typing import Final
from apps.notion.block import NotionBlock

import pytest

PATH: Final[str] = "https://prod-files-secure.s3.us-west-2.amazonaws.com/104f7d40-2db5-41f3-b01e-43d21495ac97/bd45f677-ff03-433e-852d-3f1f16c714ed/%D0%94%D0%BE%D0%BC%D0%B0%D1%88%D0%BA%D0%B0_1-2.jpg"

EXPECTED: Final[str] = "https://notion.so/image/https%3A%2F%2Fprod-files-secure.s3.us-west-2.amazonaws.com%2F104f7d40-2db5-41f3-b01e-43d21495ac97%2Fbd45f677-ff03-433e-852d-3f1f16c714ed%2F%25D0%2594%25D0%25BE%25D0%25BC%25D0%25B0%25D1%2588%25D0%25BA%25D0%25B0_1-2.jpg?table=block&id=test-block&cache=v2"


@pytest.fixture
def image_block():
    return NotionBlock(
        id="test-block",
        data={
            "value": {
                "id": "test-block",
                "type": "image",
                "format": {
                    "display_source": PATH,
                },
                "parent_id": "74c94cfa-503d-4228-88f9-4ff6c865379f",
                "properties": {
                    "source": [
                        [
                            "PATH",
                        ]
                    ]
                },
                "parent_table": "block"
            }
    })

@pytest.fixture
def page_block():
    return NotionBlock(
        id="test-block",
        data={
            "value": {
                "id": "test-block",
                "type": "page",
                "format": {
                    "page_cover": PATH,
                },
                "properties": {
                    "content": [
                        [
                            "other-block",
                        ]
                    ]
                },
                "parent_table": "block"
            }
    })



def test_image_block(image_block):
    assert get_asset_url(
        asset=PATH,
        block_data=image_block.data,
    ) == EXPECTED


def test_page_block(page_block):
    assert get_asset_url(
        asset=PATH,
        block_data=page_block.data,
    ) == EXPECTED


def test_parent_table_is_space(image_block):
    image_block.data["value"]["parent_table"] = "space"

    assert get_asset_url(
        asset=PATH,
        block_data=image_block.data,
    ) == EXPECTED


@pytest.mark.parametrize("url", [
    "https://typicalmacuser.jpg",
    "💩",
])
def test_non_notion_urls(image_block, url):
    image_block.data["value"]["properties"]["source"] = [[url]]

    assert get_asset_url(
        asset=url,
        block_data=image_block.data,
    ) == url  # should be initial URL
