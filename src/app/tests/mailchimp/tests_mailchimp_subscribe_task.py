import pytest

from app import tasks

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def mass_subscribe(mocker):
    return mocker.patch('app.integrations.mailchimp.client.AppMailchimp.mass_subscribe')


@pytest.fixture(autouse=True)
def set_tags(mocker):
    return mocker.patch('app.integrations.mailchimp.client.AppMailchimp.set_tags')


def test_task(user, mass_subscribe, mailchimp_member):
    tasks.subscribe_to_mailchimp.delay(user.pk)

    mass_subscribe.assert_called_once_with(
        list_id='123cba',
        members=[mailchimp_member],
    )


def test_particular_list_id(user, mass_subscribe, mailchimp_member):
    tasks.subscribe_to_mailchimp.delay(
        user_id=user.pk,
        list_id='TESTING-LIST-ID',
    )

    mass_subscribe.assert_called_once_with(
        list_id='TESTING-LIST-ID',
        members=[
            mailchimp_member,
        ],
    )


def test_tags(user, mailchimp_member, set_tags):
    tasks.subscribe_to_mailchimp.delay(
        user_id=user.pk,
        list_id='TESTING-LIST-ID',
        tags=['aatag', 'bbtag'],
    )

    set_tags.assert_called_once_with(
        list_id='TESTING-LIST-ID',
        member=mailchimp_member,
        tags=['aatag', 'bbtag'],
    )


def test_task_does_not_do_things_if_there_is_no_mailchimp_contact_list_id(user, mass_subscribe, settings):
    settings.MAILCHIMP_CONTACT_LIST_ID = None

    tasks.subscribe_to_mailchimp.delay(user.pk)

    mass_subscribe.assert_not_called()
