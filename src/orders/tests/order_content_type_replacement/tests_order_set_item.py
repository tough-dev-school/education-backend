import pytest

from orders.exceptions import UnknownItemException

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def order(order):
    """Empty order"""
    return order()


def test_course(order, course):
    order.set_item(course)
    order.save()

    order.refresh_from_db()

    assert order.course == course


def test_exception_when_there_is_not_foreignkey(order):
    with pytest.raises(UnknownItemException):
        order.set_item(order)


def test_setting_new_item_removes_the_old_one(order, course, another_course):
    order.set_item(course)
    order.save()

    order.set_item(another_course)
    order.save()

    order.refresh_from_db()

    assert order.course == another_course
