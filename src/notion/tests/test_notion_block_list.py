import pytest

from notion.block import NotionBlock, NotionBlockList


@pytest.fixture
def block_without_content() -> NotionBlock:
    return NotionBlock(id='without_content', data={})


@pytest.fixture
def block_with_content() -> NotionBlock:
    return NotionBlock(id='with_content', data={
        'value': {
            'content': ['a', 'b', 'c'],
        },
    })


@pytest.fixture
def another_block_with_content() -> NotionBlock:
    return NotionBlock(id='another_with_content', data={
        'value': {
            'content': ['c', 'e', 'f'],
        },
    })


def test_no_content(block_without_content):
    block_list = NotionBlockList([block_without_content])

    assert block_list.get_underlying_block_ids() == set()


def test_content(block_with_content, block_without_content):
    block_list = NotionBlockList([block_with_content, block_without_content])

    assert block_list.get_underlying_block_ids() == {'a', 'b', 'c'}


def test_block_ids_are_merged(block_with_content, another_block_with_content):
    block_list = NotionBlockList([block_with_content, another_block_with_content])

    assert block_list.get_underlying_block_ids() == {'a', 'b', 'c', 'e', 'f'}, 'should be only one "c" despite it is present in two blocks'


def test_no_recursion_on_existing_blocks(block_with_content, another_block_with_content):
    """Make sure the list does not return BlockIds that are already in the list
    """
    another_block_with_content.data['value']['content'] = ['with_content']

    block_list = NotionBlockList([block_with_content, another_block_with_content])

    assert block_list.get_underlying_block_ids() == {'a', 'b', 'c'}
