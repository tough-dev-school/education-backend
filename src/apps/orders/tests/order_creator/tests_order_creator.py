import pytest

from apps.orders.models import Order

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


def test_free_course(create, user, course):
    course.update(price=0)

    order = create(user=user, item=course)

    order.refresh_from_db()

    assert order.price == 0
    assert order.item == course
    assert order.paid is None


def test_course_manual(create, user, course):
    order = create(user=user, item=course)

    order.refresh_from_db()

    assert order.price == 100500
    assert order.item == course


@pytest.mark.parametrize("price", [0, 200500])
def test_forced_price(create, user, course, price):
    order = create(user=user, item=course, price=price)

    order.refresh_from_db()

    assert order.price == price
