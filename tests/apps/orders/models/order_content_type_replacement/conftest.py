import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def order(factory, mocker):
    mocker.patch("apps.orders.services.order_shipper.OrderShipper.write_success_admin_log")

    return lambda **kwargs: factory.order(**kwargs)
