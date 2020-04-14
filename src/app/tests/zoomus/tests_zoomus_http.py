import pytest

from app.integrations.zoomus import ZoomusHTTPException


@pytest.mark.parametrize(
    'url, expected',
    [
        ['/test/create', 'https://api.zoom.us/test/create'],
        ['test/create', 'https://api.zoom.us/test/create'],
        ['test/create/?par=val', 'https://api.zoom.us/test/create/?par=val'],
        [
            'test/create/?par=val&par1=val1',
            'https://api.zoom.us/test/create/?par=val&par1=val1',
        ],
    ],
)
def test_format_url(url, expected, client):
    assert client.http.format_url(url) == expected


def test_post_ok(client):
    client.http_mock.post('https://api.zoom.us/create/companies', json={'ok': True})

    got = client.http.post('create/companies', {'a': 'b'})

    assert got['ok'] is True


def test_post_fail(client):
    client.http_mock.post('https://api.zoom.us/create/companies', status_code=412, json={'ok': False})

    with pytest.raises(ZoomusHTTPException):
        client.http.post('create/companies', {'a': 'b'})


def test_get_ok(client):
    client.http_mock.get('https://api.zoom.us/companies', json=['cmp1', 'cmp2'])

    got = client.http.get('companies')

    assert got == ['cmp1', 'cmp2']


def test_get_fail(client):
    client.http_mock.get('https://api.zoom.us/companies', status_code=412)

    with pytest.raises(ZoomusHTTPException):
        client.http.get('companies')
