import pytest


@pytest.fixture
def order(factory, mocker):
    mocker.patch("apps.orders.services.order_shipper.OrderShipper.write_success_admin_log")

    return factory.order()
