import pytest

from app import tasks

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def mass_subscribe(mocker):
    return mocker.patch('app.integrations.mailchimp.client.AppMailchimp.mass_subscribe')


def test_task(user, mass_subscribe, mailchimp_member):
    tasks.subscribe_to_mailchimp.delay(user.pk)

    mass_subscribe.assert_called_once_with(
        list_id='123cba',
        members=[mailchimp_member],
    )


def test_particular_list_id(user, mass_subscribe, mailchimp_member):
    tasks.subscribe_to_mailchimp.delay(user.pk, list_id='TESTING-LIST-ID')

    mass_subscribe.assert_called_once_with(
        list_id='TESTING-LIST-ID',
        members=[
            mailchimp_member,
        ],
    )


def test_task_does_not_do_things_if_there_is_no_mailchimp_contact_list_id(user, mass_subscribe, settings):
    settings.MAILCHIMP_CONTACT_LIST_ID = None

    tasks.subscribe_to_mailchimp.delay(user.pk)

    mass_subscribe.assert_not_called()
