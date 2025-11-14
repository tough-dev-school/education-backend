from functools import partial

import pytest

from apps.users.services import UserEmailChanger


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User", email="old@email.com")


@pytest.fixture
def subscribe(mocker):
    return mocker.patch("apps.dashamail.lists.dto.DashamailSubscriber.subscribe")


@pytest.fixture
def service(user):
    return partial(UserEmailChanger, user=user)
