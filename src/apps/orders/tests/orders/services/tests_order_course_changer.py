import datetime

import pytest

from apps.orders.services import OrderCourseChanger

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def ship(mocker):
    return mocker.patch("apps.studying.shipment_factory.ship")


@pytest.fixture
def unship(mocker):
    return mocker.patch("apps.studying.shipment_factory.unship")


@pytest.fixture
def unshipped_order(factory, course):
    return factory.order(item=course)


@pytest.fixture
def order(unshipped_order):
    unshipped_order.ship()

    return unshipped_order


def test_changing_course_non_shipped_order(unshipped_order, another_course):
    OrderCourseChanger(order=unshipped_order, course=another_course)()

    unshipped_order.refresh_from_db()

    assert unshipped_order.course == another_course


def test_unshipped_orders_do_not_mess_with_ship(unshipped_order, another_course, ship, unship):
    OrderCourseChanger(order=unshipped_order, course=another_course)()

    assert ship.call_count == 0
    assert unship.call_count == 0


def test_chaning_course_for_shipped_order(order, another_course):
    OrderCourseChanger(order=order, course=another_course)()

    order.refresh_from_db()

    assert order.course == another_course


def test_shipped_order_is_unshipped_and_then_shipped_again(order, another_course, ship, unship):
    OrderCourseChanger(order=order, course=another_course)()

    assert ship.call_count == 1
    assert unship.call_count == 1


def test_paid_date_is_not_changed_during_course_changing(order, another_course):
    """Important business story: paid date is not altered during course change"""
    order.update(paid="2001-01-01 15:30+00:00")

    OrderCourseChanger(order=order, course=another_course)()
    order.refresh_from_db()

    assert order.paid == datetime.datetime(2001, 1, 1, 15, 30, tzinfo=datetime.timezone.utc)
