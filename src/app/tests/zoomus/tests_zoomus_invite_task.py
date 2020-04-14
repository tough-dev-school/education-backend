import pytest

from app.tasks import invite_to_zoomus

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def invite(mocker):
    return mocker.patch('app.integrations.zoomus.client.ZoomusClient.invite')


def test(invite, user):
    invite_to_zoomus.delay('https://a.test', user.id)

    invite.assert_called_once_with('https://a.test', user)
