import pytest

from app.tasks import invite_to_clickmeeting


@pytest.fixture
def invite(mocker):
    return mocker.patch('app.integrations.clickmeeting.client.ClickMeetingClient.invite')


def test(invite):
    invite_to_clickmeeting.delay('https://a.test', 'kamaz.othodov@gmail.com')

    invite.assert_called_once_with('https://a.test', 'kamaz.othodov@gmail.com')
