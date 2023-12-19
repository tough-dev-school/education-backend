import pytest

from core import current_user
from core.current_user import set_current_user, get_current_user


@pytest.fixture
def mock_order_refund_service_current_user(mocker, user):
    old_current_user = None

    def _mock_current_user(user):
        old_current_user = get_current_user()
        set_current_user(user)

    yield _mock_current_user

    set_current_user(old_current_user)


@pytest.fixture
def mock_order_shiper_service_current_user(mocker, user):
    old_current_user = None

    def _mock_current_user(user):
        old_current_user = get_current_user()
        set_current_user(user)

    yield _mock_current_user

    set_current_user(old_current_user)
