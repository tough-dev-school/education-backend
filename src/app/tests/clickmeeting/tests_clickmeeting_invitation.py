import pytest

from app.integrations.clickmeeting import ClickMeetingNonOkResponseException, ClickMeetingRoomNotFoundException


@pytest.fixture
def client(client, read_fixture):
    client.http_mock.get(
        'https://api.clickmeeting.com/v1/conferences/',
        json=read_fixture('app/tests/clickmeeting/fixtures/conferences'),
    )

    return client


ROOM_URL = 'https://f213.clickmeeting.com/tst'
INVITE_URL = 'https://api.clickmeeting.com/v1/conferences/2632756/invitation/email/ru'


def test_ok(client):
    client.http_mock.post(INVITE_URL, json={
        'status': 'OK',
    })

    client.invite(ROOM_URL, ['a@test.org', 'b@test.org'])


def test_fail(client):
    client.http_mock.post(INVITE_URL, json={
        'status': 'FuckYou',
    })

    with pytest.raises(ClickMeetingNonOkResponseException):
        client.invite(ROOM_URL, ['a@test.org', 'b@test.org'])


def test_room_not_found(client):
    with pytest.raises(ClickMeetingRoomNotFoundException):
        client.invite('https://notfound.for.test')
