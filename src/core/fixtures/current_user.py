import pytest

from core import current_user


@pytest.fixture
def _set_current_user(user):
    current_user.set_current_user(user)

    yield

    current_user.unset_current_user()
