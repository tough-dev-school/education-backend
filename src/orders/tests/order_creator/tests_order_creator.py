import pytest

from orders.creator import OrderCreator
from orders.models import Order

pytestmark = [pytest.mark.django_db]


def get_order():
    return Order.objects.last()


def create(*args, **kwargs):
    return OrderCreator(*args, **kwargs)()


def test_user(user, course):
    order = create(user=user, item=course)

    order.refresh_from_db()

    assert order.user == user


def test_course(user, course):
    order = create(user=user, item=course)

    order.refresh_from_db()

    assert order.price == 100500
    assert order.item == course


def test_record(user, record):
    order = create(user=user, item=record)

    order.refresh_from_db()

    assert order.price == 100500
    assert order.item == record


def test_course_manual(user, course):
    order = create(user=user, item=course)

    order.refresh_from_db()

    assert order.price == 100500
    assert order.item == course
