import pytest

from apps.orders.models import PromoCode

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("ten_percent_promocode"),
]


def get_annotated_promocode():
    return PromoCode.objects.with_order_count().get_or_nothing("TESTCODE")


@pytest.fixture
def another_promocode(mixer):
    return mixer.blend(PromoCode, discount_percent=15)


def test_zero():
    promocode = get_annotated_promocode()

    assert promocode.order_count == 0


def test_two(factory, ten_percent_promocode):
    factory.cycle(2).order(promocode=ten_percent_promocode, is_paid=True)

    promocode = get_annotated_promocode()

    assert promocode.order_count == 2


def test_another_promocode(factory, another_promocode):
    factory.cycle(2).order(promocode=another_promocode, is_paid=True)

    promocode = get_annotated_promocode()

    assert promocode.order_count == 0


def test_not_paid_orders(factory, ten_percent_promocode):
    factory.cycle(2).order(promocode=ten_percent_promocode, is_paid=False)

    promocode = get_annotated_promocode()

    assert promocode.order_count == 0
