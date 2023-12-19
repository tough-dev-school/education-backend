import pytest

from core import current_user


@pytest.fixture
def mock_order_refund_service_current_user(mocker, user):
    mocker.patch("apps.orders.services.order_refunder.get_current_user", return_value=user)


@pytest.fixture
def mock_order_shiper_service_current_user(mocker, user):
    mocker.patch("apps.orders.services.order_shipper.get_current_user", return_value=user)    
