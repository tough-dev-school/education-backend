import pytest

from orders.models import PromoCode

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def promocode(mixer):
    return mixer.blend(PromoCode, name='testcode')


def get_annotated_promocode():
    return PromoCode.objects.with_order_count().filter(name='testcode').first()


@pytest.fixture
def another_promocode(mixer):
    return mixer.blend(PromoCode)


def test_zero():
    promocode = get_annotated_promocode()

    assert promocode.order_count == 0


def test_two(mixer, promocode):
    mixer.cycle(2).blend('orders.Order', promocode=promocode, paid='2032-12-01 12:30')

    promocode = get_annotated_promocode()

    assert promocode.order_count == 2


def test_another_promocode(mixer, another_promocode):
    mixer.cycle(2).blend('orders.Order', promocode=another_promocode, paid='2032-12-01 12:30')

    promocode = get_annotated_promocode()

    assert promocode.order_count == 0


def test_not_paid_orders(mixer, promocode):
    mixer.cycle(2).blend('orders.Order', promocode=promocode, paid=None)

    promocode = get_annotated_promocode()

    assert promocode.order_count == 0
