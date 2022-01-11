import pytest
from django.core.cache import cache
from pytest_httpx import HTTPXMock


@pytest.fixture
def assert_all_responses_were_requested() -> bool:
    return False


@pytest.fixture(autouse=True)
def _ok(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url='https://www.notion.so/api/v3/loadPageChunk',
        json={
            'recordMap': {
                '__version__': 3,
                'block': {
                    'first-block': {
                        'role': 'editor',
                        'value': {
                            'id': 'first-block',
                            'type': 'page',
                            'properties': {
                                'title': [['Неделя 1 из 4']],
                            },
                            'content': [
                                'third-block',
                                'fourth-block',
                            ],
                        },
                    },
                    'second-block': {},
                },
            },
        },
    )


def test_request_is_done_for_the_first_time(notion, httpx_mock: HTTPXMock):
    notion.fetch_page('0cb348b3a2d24c05bc944e2302fa553')

    assert len(httpx_mock.get_requests()) == 1


def test_request_is_cached(notion, httpx_mock: HTTPXMock):
    notion.fetch_page('0cb348b3a2d24c05bc944e2302fa553')
    notion.fetch_page('0cb348b3a2d24c05bc944e2302fa553')

    assert len(httpx_mock.get_requests()) == 1


def test_request_is_cached_in_django_cache(notion, httpx_mock: HTTPXMock):
    notion.fetch_page('0cb348b3a2d24c05bc944e2302fa553')
    cache.clear()
    notion.fetch_page('0cb348b3a2d24c05bc944e2302fa553')

    assert len(httpx_mock.get_requests()) == 2
