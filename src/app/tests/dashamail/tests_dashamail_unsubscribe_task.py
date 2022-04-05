import pytest

from app import tasks

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def unsubscribe_user(mocker):
    return mocker.patch('app.integrations.dashamail.client.AppDashamail.unsubscribe_user')


def test_task(user, unsubscribe_user):
    tasks.unsubscribe_from_dashamail.delay(user.pk)

    unsubscribe_user.assert_called_once_with(
        list_id='1',
        email=user.email,
    )


def test_particular_list_id(user, unsubscribe_user):
    tasks.unsubscribe_from_dashamail.delay(
        user_id=user.pk,
        list_id='TESTING-LIST-ID',
    )

    unsubscribe_user.assert_called_once_with(
        list_id='TESTING-LIST-ID',
        email=user.email,
    )


def test_task_does_not_do_things_if_there_is_no_dashamail_contact_list_id(user, unsubscribe_user, settings):
    settings.DASHAMAIL_LIST_ID = None

    tasks.unsubscribe_from_dashamail.delay(user.pk)

    unsubscribe_user.assert_not_called()
