import pytest
from pytest_httpx import HTTPXMock


@pytest.fixture(autouse=True)
def _ok(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url='https://www.notion.so/api/v3/loadCachedPageChunk',
        json={
            'recordMap': {
                '__version__': 3,
                'block': {
                    'first-block': {},
                    'second-block': {},
                },
                'comment': {
                    'first-comment': {},
                    'second-comment': {},
                },
                'discussion': {
                    'first-discussion': {},
                    'second-discussion': {},
                },
            },
        },
    )


def test_ok(notion):
    page = notion.fetch_page('0cb348b3a2d24c05bc944e2302fa553')

    assert len(page.blocks) == 2
    assert len(page.discussions) == 2
    assert len(page.comments) == 2

    assert page.blocks[0].id == 'first-block'
    assert page.comments[0].id == 'first-comment'
    assert page.discussions[0].id == 'first-discussion'
