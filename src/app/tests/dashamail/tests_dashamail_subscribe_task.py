import pytest

from app import tasks

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def subscribe_user(mocker):
    return mocker.patch("app.integrations.dashamail.client.AppDashamail.subscribe_user")


@pytest.fixture
def get_subscriber_doesnt_exist(mocker):
    return mocker.patch("app.integrations.dashamail.client.AppDashamail.get_subscriber", return_value=(None, False))


@pytest.fixture
def get_subscriber_active(mocker):
    return mocker.patch("app.integrations.dashamail.client.AppDashamail.get_subscriber", return_value=(1337, True))


@pytest.fixture
def get_subscriber_inactive(mocker):
    return mocker.patch("app.integrations.dashamail.client.AppDashamail.get_subscriber", return_value=(1337, False))


@pytest.fixture
def update_subscriber(mocker):
    return mocker.patch("app.integrations.dashamail.client.AppDashamail.update_subscriber")


@pytest.mark.usefixtures("get_subscriber_doesnt_exist")
def test_task_when_user_didnt_exist(user, subscribe_user, update_subscriber):
    tasks.manage_subscription_to_dashamail.delay(
        list_id="1",
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=["test1", "1test"],
    )

    subscribe_user.assert_called_once_with(
        list_id="1",
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=["test1", "1test"],
    )
    update_subscriber.assert_not_called()


@pytest.mark.usefixtures("get_subscriber_active")
def test_task_when_user_exist_and_active(user, subscribe_user, update_subscriber):
    tasks.manage_subscription_to_dashamail.delay(
        list_id="1",
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=["test1", "1test"],
    )

    update_subscriber.assert_called_once_with(
        list_id="1",
        member_id=1337,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=["test1", "1test"],
    )
    subscribe_user.assert_not_called()


@pytest.mark.usefixtures("get_subscriber_inactive")
def test_task_when_user_exist_and_inactive(user, subscribe_user, update_subscriber):
    tasks.manage_subscription_to_dashamail.delay(
        list_id="1",
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=["test1", "1test"],
    )

    update_subscriber.assert_called_once_with(  # even if user unsubscribed we keep his profile actual
        list_id="1",
        member_id=1337,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=["test1", "1test"],
    )
    subscribe_user.assert_not_called()
