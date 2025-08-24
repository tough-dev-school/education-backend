from functools import partial

import pytest
from django.core.exceptions import ValidationError

from apps.users.services import UserEmailChanger

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def subscribe(mocker):
    return mocker.patch("apps.dashamail.lists.dto.DashamailSubscriber.subscribe")


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User", email="old@email.com")


@pytest.fixture
def service(user):
    return partial(UserEmailChanger, user=user)


def test_fields_are_changed(user, service):
    service(new_email="new@email.com")()

    user.refresh_from_db()

    assert user.email == "new@email.com"
    assert user.username == "new@email.com"


def test_duplicate_username_protection(service, mixer):
    mixer.blend("users.User", email="some.other@email.com", username="new@email.com")

    with pytest.raises(ValidationError):
        service(new_email="new@email.com")()


@pytest.mark.dashamail
def test_user_is_not_subscribed_by_default(service, subscribe):
    service(new_email="new@email.com")()

    assert subscribe.call_count == 0


@pytest.mark.dashamail
def test_user_is_subscribed_to_dashamail_if_subscribe_is_true(service, subscribe):
    service(new_email="new@email.com", force_subscribe=True)()

    assert subscribe.call_count == 1


def test_user_is_not_subscribed_if_dashamail_is_disabled(service, subscribe):
    """Same as above, but without enabling dashamail"""
    service(new_email="new@email.com", force_subscribe=True)()

    assert subscribe.call_count == 0
