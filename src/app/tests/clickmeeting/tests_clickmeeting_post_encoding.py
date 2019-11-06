"""This is a test suite for ugly build_query function copy-pasted from clickmeeting API examples

Consider it a snapshot test
"""
import pytest


@pytest.mark.parametrize('input, expected', [
    [dict(a='b'), 'a=b'],
    [dict(a=dict(a='b')), 'a%5Ba%5D=b'],
    [dict(a=dict(a='b'), c=['d', 'e']), 'a%5Ba%5D=b&c[]=d&c[]=e'],
])
def test(client, input, expected):
    assert client.http.build_query(input) == expected
