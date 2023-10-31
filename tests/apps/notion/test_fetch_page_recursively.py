import pytest

from apps.notion.block import NotionBlock
from apps.notion.block import NotionBlockList
from apps.notion.page import NotionPage


@pytest.fixture
def page() -> NotionPage:
    return NotionPage(
        blocks=NotionBlockList(
            [
                NotionBlock(
                    id="block1",
                    data={
                        "value": {
                            "content": ["block2", "block3"],
                        },
                    },
                ),
            ]
        ),
    )


def test_one_pass(notion, page, fetch_page, fetch_blocks):
    fetch_page.return_value = page
    fetch_blocks.return_value = NotionBlockList([NotionBlock(id="block2", data={}), NotionBlock(id="block3", data={})])

    fetched = notion.fetch_page_recursively("100500")

    assert fetched.blocks.have_block_with_id("block2")
    assert fetched.blocks.have_block_with_id("block3")


def test_two_passes(notion, page, fetch_page, fetch_blocks):
    fetch_page.return_value = page
    fetch_blocks.side_effect = [
        NotionBlockList([NotionBlock(id="block2", data={"value": {"content": ["block4", "block5"]}})]),
        NotionBlockList([NotionBlock(id="block4", data={}), NotionBlock(id="block5", data={})]),
    ]

    fetched = notion.fetch_page_recursively("100500")

    assert fetched.blocks.have_block_with_id("block4")
    assert fetched.blocks.have_block_with_id("block5")


def test_fetching_does_not_get_stuck_in_inifinite_loop_when_notion_does_not_return_one_of_requested_blocks(notion, page, fetch_page, fetch_blocks):
    fetch_page.return_value = page
    fetch_blocks.return_value = NotionBlockList([NotionBlock(id="block2", data={})])  # return only block2, despite requested block2 and block3

    notion.fetch_page_recursively("100500")

    fetch_page.assert_called_once()
