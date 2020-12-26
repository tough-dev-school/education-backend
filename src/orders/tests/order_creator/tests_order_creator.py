import pytest

from orders.models import Order

pytestmark = [pytest.mark.django_db]


def get_order():
    return Order.objects.last()


def test_user(create, user, course):
    order = create(user=user, item=course)

    order.refresh_from_db()

    assert order.user == user


def test_course(create, user, course):
    order = create(user=user, item=course)

    order.refresh_from_db()

    assert order.price == 100500
    assert order.item == course


def test_record(create, user, record):
    order = create(user=user, item=record)

    order.refresh_from_db()

    assert order.price == 100500
    assert order.item == record


def test_course_manual(create, user, course):
    order = create(user=user, item=course)

    order.refresh_from_db()

    assert order.price == 100500
    assert order.item == course
