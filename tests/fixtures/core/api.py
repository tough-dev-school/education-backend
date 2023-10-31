import pytest
from typing import Callable

from core.test.api_client import DRFClient
from apps.users.models import User


@pytest.fixture
def api():
    return DRFClient()


@pytest.fixture
def anon():
    return DRFClient(anon=True)


@pytest.fixture
def as_() -> Callable[[User | None], DRFClient]:
    def as_who(user: User | None = None) -> DRFClient:
        return DRFClient(user=user, god_mode=False)

    return as_who


@pytest.fixture
def as_superuser(as_: "Callable[[User | None], DRFClient]", user: "User") -> "DRFClient":
    user.update(is_staff=True, is_superuser=True)

    return as_(user)


@pytest.fixture
def as_user(as_: Callable, user: User) -> DRFClient:
    return as_(user)
