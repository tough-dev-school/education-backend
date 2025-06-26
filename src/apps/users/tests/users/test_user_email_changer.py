from functools import partial

import pytest
from django.core.exceptions import ValidationError

from apps.users.services import UserEmailChanger

pytestmark = [pytest.mark.django_db]


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
