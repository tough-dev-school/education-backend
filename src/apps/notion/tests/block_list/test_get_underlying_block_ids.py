from apps.notion.block import NotionBlockList


def test_no_content(block_without_content):
    block_list = NotionBlockList([block_without_content])

    assert block_list.get_underlying_block_ids() == set()


def test_content(block_with_content, block_without_content):
    block_list = NotionBlockList([block_with_content, block_without_content])

    assert block_list.get_underlying_block_ids() == {"a", "b", "c"}


def test_block_ids_are_merged(block_with_content, another_block_with_content):
    block_list = NotionBlockList([block_with_content, another_block_with_content])

    assert block_list.get_underlying_block_ids() == {"a", "b", "c", "e", "f"}, 'should be only one "c" despite it is present in two blocks'


def test_first_page_block_content_is_merged(block_with_content, page_block):
    block_list = NotionBlockList([page_block, block_with_content])

    assert block_list.get_underlying_block_ids() == {"a", "b", "c", "g", "h", "i"}, "content from the page should be added"


def test_non_first_blocks_with_page_type_are_ignored(block_with_content, page_block, another_block_with_content):
    another_block_with_content.data["value"]["type"] = "page"

    block_list = NotionBlockList([block_with_content, page_block, another_block_with_content])

    assert block_list.get_underlying_block_ids() == {"a", "b", "c", "g", "h", "i"}, "another_block_with_content should be ignored"


def test_no_recursion_on_existing_blocks(block_with_content, another_block_with_content):
    """Make sure the list does not return BlockIds that are already in the list"""
    another_block_with_content.data["value"]["content"] = ["with_content"]

    block_list = NotionBlockList([block_with_content, another_block_with_content])

    assert block_list.get_underlying_block_ids() == {"a", "b", "c"}
