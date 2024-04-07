from decimal import Decimal

import pytest

from apps.orders.models import Order

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(course):
    return course.update(price=0)


def get_order() -> Order | None:
    return Order.objects.last()


def test_order_is_created(call_purchase, course):
    call_purchase(desired_bank="zero_price", redirect_url="https://thank.you")

    placed = get_order()

    assert placed.item == course
    assert placed.price == Decimal(0)
    assert placed.paid is None
    assert placed.bank_id == "zero_price"
    assert placed.acquiring_percent == 0
    assert placed.ue_rate == 1


def test_redirect(call_purchase):
    response = call_purchase(as_response=True)

    assert response.status_code == 302
    assert response["Location"] == "https://bank.test/pay/"
