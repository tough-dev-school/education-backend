import pytest

from orders.services import OrderUnpaidSetter

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def paid_order(factory):
    return factory.order(is_paid=True)


def test_set_not_paid_call_service_and_set_base_attributes(paid_order, mocker):
    spy_unpaid_setter = mocker.spy(OrderUnpaidSetter, "__call__")

    paid_order.set_not_paid()

    paid_order.refresh_from_db()
    assert paid_order.paid is None
    assert paid_order.shipped is None
    spy_unpaid_setter.assert_called_once()
