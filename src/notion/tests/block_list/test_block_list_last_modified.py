from datetime import datetime

from notion.block import NotionBlockList


def test_no_last_modified(block_without_content):
    block_list = NotionBlockList([block_without_content])

    assert block_list.last_modified is None


def test_last_modified_is_max_value(block_with_content, another_block_with_content):
    block_list = NotionBlockList([block_with_content, another_block_with_content])

    assert block_list.last_modified == datetime(2022, 1, 16, 21, 11, 2)


def test_order_does_not_matter(block_with_content, another_block_with_content):
    block_list = NotionBlockList([another_block_with_content, another_block_with_content])

    assert block_list.last_modified == datetime(2022, 1, 16, 21, 11, 2)


def test_a_block_without_last_modified_does_not_break_things(block_with_content, block_without_content):
    block_list = NotionBlockList([block_with_content, block_without_content])

    assert block_list.last_modified == datetime(2022, 1, 16, 21, 11, 1)
