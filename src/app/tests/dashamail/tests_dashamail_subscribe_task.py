import pytest

from app import tasks

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def update_subscription(mocker):
    return mocker.patch('app.integrations.dashamail.client.AppDashamail.subscribe_user')


def test_task(user, update_subscription):
    tasks.subscribe_to_dashamail.delay(
        list_id='1',
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=['test1', '1test'],
    )

    update_subscription.assert_called_once_with(
        list_id='1',
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=['test1', '1test'],
    )
