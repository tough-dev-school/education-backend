import pytest


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User")


@pytest.fixture
def another_user(mixer):
    return mixer.blend("users.User")
