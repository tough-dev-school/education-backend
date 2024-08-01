import pytest

from apps.notion.block import NotionBlock, NotionBlockList
from apps.notion.models import NotionAsset
from apps.notion.page import NotionPage

pytestmark = [
    pytest.mark.django_db,
]


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


@pytest.fixture
def _mock_fetching_asset(respx_mock):
    respx_mock.post("http://notion.middleware/v1/asset/").respond(content=b"typical")


def test_one_pass(notion, page, fetch_page, fetch_blocks):
    fetch_page.return_value = page
    fetch_blocks.return_value = NotionBlockList([NotionBlock(id="block2", data={}), NotionBlock(id="block3", data={})])

    fetched = notion.fetch_page_recursively(page_id="100500")

    assert fetched.blocks.have_block_with_id("block2")
    assert fetched.blocks.have_block_with_id("block3")


def test_two_passes(notion, page, fetch_page, fetch_blocks):
    fetch_page.return_value = page
    fetch_blocks.side_effect = [
        NotionBlockList([NotionBlock(id="block2", data={"value": {"content": ["block4", "block5"]}})]),
        NotionBlockList([NotionBlock(id="block4", data={}), NotionBlock(id="block5", data={})]),
    ]

    fetched = notion.fetch_page_recursively(page_id="100500")

    assert fetched.blocks.have_block_with_id("block4")
    assert fetched.blocks.have_block_with_id("block5")


def test_fetching_does_not_get_stuck_in_inifinite_loop_when_notion_does_not_return_one_of_requested_blocks(notion, page, fetch_page, fetch_blocks):
    fetch_page.return_value = page
    fetch_blocks.return_value = NotionBlockList([NotionBlock(id="block2", data={})])  # return only block2, despite requested block2 and block3

    notion.fetch_page_recursively(page_id="100500")

    fetch_page.assert_called_once()


@pytest.mark.usefixtures("_mock_fetching_asset")
def test_assets_are_fetched(notion, page, fetch_page, fetch_blocks):
    fetch_page.return_value = page
    fetch_blocks.side_effect = [
        NotionBlockList(
            [
                NotionBlock(
                    id="block2",
                    data={
                        "value": {
                            "id": "block2",
                            "type": "image",
                            "properties": {
                                "source": [["https://secure.notion-static.com/typicalmacuser.jpg"]],
                            },
                            "parent_table": "test-table",
                        }
                    },
                )
            ]
        ),
    ]

    notion.fetch_page_recursively(page_id="100500")

    fetched_asset = NotionAsset.objects.get(url="https://secure.notion-static.com/typicalmacuser.jpg")

    assert fetched_asset.file.read() == b"typical"
