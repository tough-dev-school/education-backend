from functools import partial

import pytest

from apps.users.services import UserEmailChanger

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User", email="old@email.com")


@pytest.fixture
def service(user):
    return partial(UserEmailChanger, user=user)


def test_email_is_changed(user, service):
    service(new_email="new@email.com")()

    user.refresh_from_db()

    assert user.email == "new@email.com"
