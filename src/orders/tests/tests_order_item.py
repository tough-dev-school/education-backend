import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def order(mixer):
    return lambda **kwargs: mixer.blend('orders.Order', **kwargs)


def test_order_without_items(order):
    order = order()

    assert order.item is None


def test_order_with_record(order, record):
    order = order(record=record)

    assert order.item == record


def test_order_with_course(order, course):
    order = order(course=course)

    assert order.item == course
