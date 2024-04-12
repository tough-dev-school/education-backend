import pytest

pytestmark = [pytest.mark.django_db]


def test_empty_order(order, course):
    order = order()

    field = order.get_item_foreignkey(course)

    assert field == "course"


def test_order_with_course(order, course):
    order = order(item=course)

    field = order.get_item_foreignkey(course)

    assert field == "course"
