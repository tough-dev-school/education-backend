import pytest


@pytest.fixture
def user(factory):
    return factory.user()


@pytest.fixture
def another_user(mixer):
    return mixer.blend("users.User")
