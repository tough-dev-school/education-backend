from decimal import Decimal

import pytest

from apps.orders.models import Order

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("usd"),
]


def test_orders_are_created(completer, factory):
    completer(deal=factory.deal(student_count=3))()

    assert Order.objects.count() == 3


def test_order_data_for_created_orders(completer, factory):
    deal = factory.deal(student_count=1)

    completer(deal=deal)()
    order = Order.objects.first()

    assert order.deal == deal, "Order should be linked to the deal"
    assert order.author == deal.author
    assert order.user == deal.students.first().user
    assert order.item == deal.course
    assert order.bank_id == "b2b"


def test_orders_are_paid_and_shipped(completer, factory):
    deal = factory.deal(student_count=1)

    completer(deal=deal)()
    order = Order.objects.first()

    assert order.paid is not None
    assert order.shipped is not None


def test_created_orders_are_paid(completer, factory):
    completer(deal=factory.deal(student_count=1))()
    order = Order.objects.first()

    assert order.paid is not None


@pytest.mark.parametrize(
    ("student_count", "single_order_price"),
    [
        (1, "100.50"),
        (3, "33.50"),
        (4, "25.13"),
        (5, "20.10"),
    ],
)
def test_price_calculation(completer, factory, student_count, single_order_price):
    deal = factory.deal(student_count=student_count, price=Decimal("100.50"))

    completer(deal=deal)()
    order = Order.objects.first()

    assert str(order.price) == single_order_price


@pytest.mark.usefixtures("usd")
@pytest.mark.parametrize(
    ("currency", "single_order_price"),
    [
        ("RUB", "50.00"),
        ("USD", "5000.00"),
        ("NNE", "50.00"),  # for nonexistant currencis the default rate is used
    ],
)
def test_currency_price_calculation(completer, factory, currency, single_order_price):
    deal = factory.deal(student_count=2, price=Decimal("100.00"), currency=currency)

    completer(deal=deal)()
    order = Order.objects.first()

    assert str(order.price) == single_order_price


def test_zero_price(factory):
    deal = factory.deal(student_count=0, price=Decimal(0))
    assert deal.get_single_order_price() == 0
