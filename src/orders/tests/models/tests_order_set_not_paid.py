from datetime import datetime
from datetime import timezone
import pytest

from orders.services import OrderRefunder

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def paid_order(factory):
    return factory.order(is_paid=True)


@pytest.mark.freeze_time("2022-04-19 19:23Z")
def test_set_not_paid_call_service_and_set_base_attributes(paid_order, mocker):
    spy_refunder = mocker.spy(OrderRefunder, "__call__")

    paid_order.set_not_paid()

    paid_order.refresh_from_db()
    assert paid_order.paid is None
    assert paid_order.shipped is None
    assert paid_order.unpaid == datetime(2022, 4, 19, 19, 23, tzinfo=timezone.utc)
    spy_refunder.assert_called_once()
