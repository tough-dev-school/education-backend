import pytest

from app.integrations.dashamail.subscription_updater import SubscriptionUpdater

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def updater():
    return SubscriptionUpdater


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


@pytest.mark.usefixtures("get_subscriber_active")
def test_user_is_updated_when_he_exists(user, subscribe_user, update_subscriber, updater):
    user.tags = ["popug-3-self__purchased", "any-purchase"]
    user.save()

    updater(user)()

    update_subscriber.assert_called_once_with(
        member_id=1337,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=["popug-3-self__purchased", "any-purchase"],
    )
    subscribe_user.assert_not_called()


@pytest.mark.usefixtures("get_subscriber_doesnt_exist")
def test_user_gets_subscribed_when_he_didnt_exist(user, subscribe_user, update_subscriber, updater):
    user.tags = ["popug-3-self__purchased", "any-purchase"]
    user.save()

    updater(user)()

    update_subscriber.assert_not_called()
    subscribe_user.assert_called_once_with(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=["popug-3-self__purchased", "any-purchase"],
    )


@pytest.mark.usefixtures("get_subscriber_inactive")
def test_user_is_updated_when_he_exist_and_inactive(user, subscribe_user, update_subscriber, updater):
    updater(user)()

    update_subscriber.assert_called_once_with(  # even if user has unsubscribed we keep his profile in actual state
        member_id=1337,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=[],
    )
    subscribe_user.assert_not_called()
