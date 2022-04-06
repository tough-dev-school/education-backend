import pytest

from app import tasks

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def unsubscribe_user(mocker):
    return mocker.patch('app.integrations.dashamail.client.AppDashamail.unsubscribe_user')


def test_task(user, unsubscribe_user):
    tasks.unsubscribe_from_dashamail.delay(email=user.email)

    unsubscribe_user.assert_called_once_with(email=user.email)
