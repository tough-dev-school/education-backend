import pytest

from app import tasks

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def subscribe(mocker):
    return mocker.patch('app.integrations.mailchimp.AppMailchimp.subscribe')


def test_task(subscribe, user):
    tasks.subscribe_to_mailchimp.delay(user.pk)

    subscribe.assert_called_once_with(user)
