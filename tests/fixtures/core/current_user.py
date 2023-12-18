import pytest

from core import current_user


@pytest.fixture
def current_user(mocker, user):
    mocker.patch("core.current_user.get_current_user", return_value=user)
