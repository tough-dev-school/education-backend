import pytest


@pytest.fixture
def client(client, read_fixture):

    client.http_mock.get(
        'https://api.clickmeeting.com/v1/conferences/',
        json=read_fixture('app/tests/clickmeeting/fixtures/conferences'),
    )

    return client


def test_find_by_1(client):
    got = client.get_conference(id=2632756)

    assert got['id'] == 2632756


def test_find_by_2(client):
    got = client.get_conference(id=2632756, name='Тестовое мероприятие')

    assert got['id'] == 2632756


@pytest.mark.parametrize('query', [
    dict(id=100500),
    dict(id=2632756, name='Всемирный съезд лохов'),
    dict(id=2632756, nonexistant_Field='Всемирный съезд лохов'),
])
def test_not_found(client, query):
    got = client.get_conference(**query)

    assert got is None
