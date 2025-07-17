from decimal import Decimal
from functools import partial

import pytest

from apps.orders.models import Order

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def order(factory, seller):
    return partial(factory.order, author=seller)


def test_order_data_for_asigned_orders(completer, factory, order):
    deal = factory.deal(student_count=1, price=100)
    existing_order = order(user=deal.students.first().user, item=deal.course, price=500)

    completer(deal=deal)()
    existing_order.refresh_from_db()

    assert Order.objects.count() == 1, "No new orders created"
    assert existing_order.deal == deal, "Order deal should be updated"
    assert existing_order.author == deal.author, "Author should be updated"
    assert existing_order.price == Decimal(500), "Price should remain the same"


def test_asigned_orders_are_paid(completer, factory, order):
    deal = factory.deal(student_count=1)
    existing_order = order(user=deal.students.first().user, item=deal.course)

    completer(deal=deal)()
    existing_order.refresh_from_db()

    assert existing_order.paid is not None
    assert existing_order.shipped is not None


def test_paid_orders_are_ignored_during_order_asignment(completer, factory, order):
    deal = factory.deal(student_count=1)
    existing_order = order(user=deal.students.first().user, item=deal.course)
    existing_order.set_paid()

    completer(deal=deal)()
    existing_order.refresh_from_db()

    assert existing_order.deal is None


def test_shipped_but_not_paid_orders_are_not_ignored_during_order_asignment(completer, factory, order):
    deal = factory.deal(student_count=1)
    existing_order = order(user=deal.students.first().user, item=deal.course)
    existing_order.ship_without_payment()

    completer(deal=deal)()
    existing_order.refresh_from_db()

    assert existing_order.deal == deal


def test_orders_with_another_courses_are_ignored(completer, factory, order, another_course):
    deal = factory.deal(student_count=1)
    existing_order = order(user=deal.students.first().user, item=another_course)

    completer(deal=deal)()
    existing_order.refresh_from_db()

    assert existing_order.deal is None


def test_self_created_orders_are_ignored(completer, factory):
    deal = factory.deal(student_count=1)
    student = deal.students.first().user
    existing_order = factory.order(user=student, author=student, item=deal.course)

    completer(deal=deal)()
    existing_order.refresh_from_db()

    assert existing_order.deal is None
