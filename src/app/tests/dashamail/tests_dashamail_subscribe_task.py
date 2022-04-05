import pytest

from app import tasks

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def update_subscription(mocker):
    return mocker.patch('app.integrations.dashamail.client.AppDashamail.update_subscription')


def test_task(user, update_subscription, dashamail_member):
    dashamail_member.tags = None

    tasks.subscribe_to_dashamail.delay(user.pk)

    update_subscription.assert_called_once_with(
        list_id='1',
        member=dashamail_member,
    )


def test_particular_list_id(user, update_subscription, dashamail_member):
    dashamail_member.tags = None

    tasks.subscribe_to_dashamail.delay(
        user_id=user.pk,
        list_id='TESTING-LIST-ID',
    )

    update_subscription.assert_called_once_with(
        list_id='TESTING-LIST-ID',
        member=dashamail_member,
    )


def test_tags(user, dashamail_member, update_subscription):
    dashamail_member.tags = ['aatag', 'bbtag']

    tasks.subscribe_to_dashamail.delay(
        user_id=user.pk,
        list_id='TESTING-LIST-ID',
        tags=['aatag', 'bbtag'],
    )

    update_subscription.assert_called_once_with(
        list_id='TESTING-LIST-ID',
        member=dashamail_member,
    )


def test_task_does_not_do_things_if_there_is_no_dashamail_contact_list_id(user, update_subscription, settings):
    settings.DASHAMAIL_LIST_ID = None

    tasks.subscribe_to_dashamail.delay(user.pk)

    update_subscription.assert_not_called()
