import pytest

from app import tasks

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def subscribe(mocker):
    return mocker.patch('app.integrations.mailchimp.AppMailchimp.subscribe')


def test_task(subscribe, user):
    tasks.subscribe_to_mailchimp.delay(user.pk)

    subscribe.assert_called_once_with(user)


def test_task_does_not_do_things_if_there_is_no_mailchimp_contact_list_id(subscribe, user, settings):
    settings.MAILCHIMP_CONTACT_LIST_ID = None

    tasks.subscribe_to_mailchimp.delay(user.pk)

    subscribe.assert_not_called()
