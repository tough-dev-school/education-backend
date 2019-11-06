import pytest

from app.clickmeeting import ClickMeetingNonOkResponseException


def test_ok(client):
    client.http_mock.post('https://api.clickmeeting.com/v1/conferences/100500/invitation/email/ru/', json={
        'status': 'OK',
    })

    client.invite('100500', ['a@test.org', 'b@test.org'])


def test_fail(client):
    client.http_mock.post('https://api.clickmeeting.com/v1/conferences/100500/invitation/email/ru/', json={
        'status': 'FuckYou',
    })

    with pytest.raises(ClickMeetingNonOkResponseException):
        client.invite('100500', ['a@test.org', 'b@test.org'])
