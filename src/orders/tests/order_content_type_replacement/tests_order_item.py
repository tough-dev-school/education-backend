import pytest

pytestmark = [pytest.mark.django_db]


def test_order_without_items(order):
    order = order()

    assert order.item is None


def test_order_with_course(order, course):
    order = order(course=course)

    assert order.item == course
