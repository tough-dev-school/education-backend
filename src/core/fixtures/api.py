import pytest

from core.test.api_client import DRFClient


@pytest.fixture
def api():
    return DRFClient()


@pytest.fixture
def anon():
    return DRFClient(anon=True)


@pytest.fixture
def as_():
    def as_who(user=None):
        return DRFClient(user=user, god_mode=False)

    return as_who


@pytest.fixture
def as_user(as_, user):
    return as_(user)
