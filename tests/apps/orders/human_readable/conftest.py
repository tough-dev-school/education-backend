import pytest

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def order(factory, course, mocker, user):
    mocker.patch("apps.orders.services.order_shipper.OrderShipper.write_success_admin_log")

    order = factory.order(user=user, price=1500)
    order.set_item(course)

    return order
