import pytest

pytestmark = [pytest.mark.django_db]


def test_empty_order(order, record):
    order = order()

    field = order.get_item_foreignkey(record)

    assert field == "record"


def test_order_with_record(order, record):
    order = order(record=record)

    field = order.get_item_foreignkey(record)

    assert field == "record"


def test_order_with_course(order, course):
    order = order(course=course)

    field = order.get_item_foreignkey(course)

    assert field == "course"
