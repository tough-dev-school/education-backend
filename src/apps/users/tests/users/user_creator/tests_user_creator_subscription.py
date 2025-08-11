import pytest

from apps.users.services import UserCreator

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def subscribe(mocker):
    return mocker.patch("apps.dashamail.lists.dto.DashamailSubscriber.subscribe")


@pytest.mark.dashamail
def test_user_is_not_subscribed_by_default(subscribe):
    UserCreator(name="test", email="test@test.org")()

    assert subscribe.call_count == 0


@pytest.mark.dashamail
def test_user_is_subscribed_if_force_subscribe_is_set(subscribe):
    UserCreator(name="test", email="test@test.org", force_subscribe=True)()

    assert subscribe.call_count == 1


def test_user_is_not_subscribed_if_dashamail_is_disabled(subscribe):
    """Same as above, but without enabling dashamail"""
    UserCreator(name="test", email="test@test.org", force_subscribe=True)()

    assert subscribe.call_count == 0
