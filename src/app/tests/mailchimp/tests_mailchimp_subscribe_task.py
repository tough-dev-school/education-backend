import pytest

from app import tasks

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def mass_update_subscription(mocker):
    return mocker.patch('app.integrations.mailchimp.client.AppMailchimp.mass_update_subscription')


@pytest.fixture(autouse=True)
def set_tags(mocker):
    return mocker.patch('app.integrations.mailchimp.client.AppMailchimp.set_tags')


def test_task(user, mass_update_subscription, mailchimp_member):
    tasks.subscribe_to_mailchimp.delay(user.pk)

    mass_update_subscription.assert_called_once_with(
        list_id='123cba',
        members=[mailchimp_member],
        status='subscribed',
    )


def test_particular_list_id(user, mass_update_subscription, mailchimp_member):
    tasks.subscribe_to_mailchimp.delay(
        user_id=user.pk,
        list_id='TESTING-LIST-ID',
    )

    mass_update_subscription.assert_called_once_with(
        list_id='TESTING-LIST-ID',
        members=[
            mailchimp_member,
        ],
        status='subscribed',
    )


def test_tags(user, mailchimp_member, set_tags):
    tasks.subscribe_to_mailchimp.delay(
        user_id=user.pk,
        list_id='TESTING-LIST-ID',
        tags=['aatag', 'bbtag'],
    )

    set_tags.assert_called_once_with(
        list_id='TESTING-LIST-ID',
        members=[mailchimp_member],
        tags=['aatag', 'bbtag'],
    )


def test_task_does_not_do_things_if_there_is_no_mailchimp_contact_list_id(user, mass_update_subscription, settings):
    settings.MAILCHIMP_CONTACT_LIST_ID = None

    tasks.subscribe_to_mailchimp.delay(user.pk)

    mass_update_subscription.assert_not_called()
