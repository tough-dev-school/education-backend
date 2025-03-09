from decimal import Decimal

import pytest

from apps.orders.models import Order

pytestmark = [pytest.mark.django_db]


def test_order_data_for_asigned_orders(completer, factory):
    deal = factory.deal(student_count=1, price=100)
    existing_order = factory.order(user=deal.students.first().user, item=deal.course, price=500)

    completer(deal=deal)()
    existing_order.refresh_from_db()

    assert Order.objects.count() == 1, "No new orders created"
    assert existing_order.deal == deal, "Order deal should be updated"
    assert existing_order.author == deal.author, "Author should be updated"
    assert existing_order.price == Decimal(500), "Price should remain the same"


def test_asigned_orders_are_paid(completer, factory):
    deal = factory.deal(student_count=1)
    existing_order = factory.order(user=deal.students.first().user, item=deal.course)

    completer(deal=deal)()
    existing_order.refresh_from_db()

    assert existing_order.paid is not None


def test_paid_orders_are_ignored_during_order_asignment(completer, factory):
    deal = factory.deal(student_count=1)
    existing_order = factory.order(user=deal.students.first().user, item=deal.course)
    existing_order.set_paid()

    completer(deal=deal)()
    existing_order.refresh_from_db()

    assert existing_order.deal is None, "Deal has not been changed, hence the order is ignored"


def test_orders_with_another_courses_are_ignored(completer, factory, another_course):
    deal = factory.deal(student_count=1)
    existing_order = factory.order(user=deal.students.first().user, item=another_course)

    completer(deal=deal)()
    existing_order.refresh_from_db()

    assert existing_order.deal is None, "Deal has not been changed, hence the order is ignored"
