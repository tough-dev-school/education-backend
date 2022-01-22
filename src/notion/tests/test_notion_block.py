import pytest
import pytz
from datetime import datetime

from notion.block import NotionBlock


@pytest.mark.parametrize(('block', 'expected_type'), [
    ({}, None),
    ({'value': {'test': 'zero'}}, None),
    ({'value': {'type': 'testing'}}, 'testing'),
])
def test_block_type(block, expected_type):
    assert NotionBlock(id='test', data=block).type == expected_type


@pytest.mark.parametrize(('block', 'expected_content'), [
    ({}, []),
    ({'value': {'test': 'zero'}}, []),
    ({'value': {'content': ['a', 'b']}}, ['a', 'b']),
])
def test_content(block, expected_content):
    assert NotionBlock(id='test', data=block).content == expected_content


@pytest.mark.parametrize(('block', 'expected_last_modified'), [
    ({}, None),
    ({'value': {'test': 'zero'}}, None),
    ({'value': {'last_edited_time': 1642356661000}}, datetime(2022, 1, 16, 21, 11, 1, tzinfo=pytz.UTC)),
])
def test_last_modified(block, expected_last_modified):
    assert NotionBlock(id='test', data=block).last_modified == expected_last_modified
