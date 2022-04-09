import pytest
from django.conf import settings

from app.integrations.dashamail.helpers import subscribe_user_to_dashamail

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def subscribe_to_dashamail(mocker):
    return mocker.patch('app.tasks.dashamail.subscribe_to_dashamail.delay')


def test(user, subscribe_to_dashamail):
    subscribe_user_to_dashamail(list_id='test-list-id', user=user, tags=['test', 'test1'])

    subscribe_to_dashamail.assert_called_once_with(
        list_id='test-list-id',
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=['test', 'test1'],
    )


def test_dont_pass_list_id(user, subscribe_to_dashamail):
    subscribe_user_to_dashamail(user=user)

    subscribe_to_dashamail.assert_called_once_with(
        list_id='1',
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=None,
    )


def test_not_called_without_list_id(user, subscribe_to_dashamail):
    settings.DASHAMAIL_LIST_ID = None

    subscribe_user_to_dashamail(user=user)

    subscribe_to_dashamail.assert_not_called()
