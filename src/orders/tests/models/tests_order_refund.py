from datetime import datetime
from datetime import timezone
import pytest

from orders.services import OrderRefunder

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def paid_order(factory):
    return factory.order(is_paid=True)


@pytest.mark.freeze_time("2022-04-19 19:23Z")
def test_set_payment_and_shipment_attributes(paid_order):
    paid_order.refund()

    paid_order.refresh_from_db()
    assert paid_order.paid is None
    assert paid_order.shipped is None
    assert paid_order.unpaid == datetime(2022, 4, 19, 19, 23, tzinfo=timezone.utc)


def test_refund_actually_call_refunder_service(paid_order, mocker):
    spy_refunder = mocker.spy(OrderRefunder, "__call__")

    paid_order.refund()

    spy_refunder.assert_called_once()
    called_service = spy_refunder.call_args.args[0]
    assert called_service.order == paid_order
