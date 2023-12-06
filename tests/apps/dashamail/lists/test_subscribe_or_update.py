import pytest

pytestmark = [pytest.mark.django_db]



@pytest.fixture
def subscribe(mocker):
    return mocker.patch("apps.dashamail.lists.client.DashamailListsClient._subscribe")


@pytest.fixture
def nonexistant_subscriber(mocker):
    return mocker.patch("apps.dashamail.lists.client.DashamailListsClient._get_member_id", return_value=(None, False))


@pytest.fixture
def active_subscriber(mocker):
    return mocker.patch("apps.dashamail.lists.client.DashamailListsClient._get_member_id", return_value=(1337, True))


@pytest.fixture
def inactive_subscriber(mocker):
    return mocker.patch("apps.dashamail.lists.client.DashamailListsClient._get_member_id", return_value=(1337, False))


@pytest.fixture
def update_subscriber(mocker):
    return mocker.patch("apps.dashamail.lists.client.DashamailListsClient._update_subscriber")


@pytest.mark.usefixtures("active_subscriber")
def test_user_is_updated_when_he_exists(dashamail, user, subscribe, update_subscriber):
    user.update(tags=["popug-3-self__purchased", "any-purchase"])

    dashamail.subscribe_or_update(user)

    update_subscriber.assert_called_once_with(
        member_id=1337,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=["popug-3-self__purchased", "any-purchase"],
    )
    subscribe.assert_not_called()


@pytest.mark.usefixtures("nonexistant_subscriber")
def test_user_gets_subscribed_when_he_didnt_exist(dashamail, user, subscribe, update_subscriber):
    user.update(tags=["popug-3-self__purchased", "any-purchase"])

    dashamail.subscribe_or_update(user)

    update_subscriber.assert_not_called()
    subscribe.assert_called_once_with(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=["popug-3-self__purchased", "any-purchase"],
    )


@pytest.mark.usefixtures("inactive_subscriber")
def test_user_is_updated_when_he_exist_and_inactive(dashamail, user, subscribe, update_subscriber):
    dashamail.subscribe_or_update(user)

    update_subscriber.assert_called_once_with(  # even if user has unsubscribed we keep his profile in actual state
        member_id=1337,
        first_name=user.first_name,
        last_name=user.last_name,
        tags=[],
    )
    subscribe.assert_not_called()
