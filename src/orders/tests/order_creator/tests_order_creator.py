import pytest
from datetime import datetime, timedelta, timezone
from django.conf import settings
from zoneinfo import ZoneInfo

from orders.models import Order
from orders.services.order_creator import OrderCreatorException

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
    course.setattr_and_save('price', 0)

    order = create(user=user, item=course)

    order.refresh_from_db()

    assert order.price == 0
    assert order.item == course
    assert order.paid is None


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


@pytest.mark.parametrize('price', [0, 200500])
def test_forced_price(create, user, course, price):
    order = create(user=user, item=course, price=price)

    order.refresh_from_db()

    assert order.price == price


@pytest.mark.parametrize(('desired_shipment_date', 'saved_date'), [
    (None, None),
    ('2022-10-10 12:40', datetime(2022, 10, 10, 12, 40, tzinfo=ZoneInfo(settings.TIME_ZONE))),  # string without timezone saved as datetime with default timezone
    ('2022-10-10 12:40+03:00', datetime(2022, 10, 10, 12, 40, tzinfo=timezone(timedelta(hours=3)))),  # pay respect for timezone in string
    ('2022-10-10 12:40-12:00', datetime(2022, 10, 10, 12, 40, tzinfo=timezone(timedelta(hours=-12)))),  # negative timezone saved right
    ('2022-10-10 12:40Z', datetime(2022, 10, 10, 12, 40, tzinfo=timezone.utc)),  # utc timezone could be passed with `Z`
    (datetime(2022, 10, 10, 15, 10), datetime(2022, 10, 10, 15, 10, tzinfo=ZoneInfo(settings.TIME_ZONE))),  # datetime without timezone saved with default timezone
    (datetime(2022, 10, 10, 15, 10, tzinfo=ZoneInfo('Asia/Magadan')), datetime(2022, 10, 10, 15, 10, tzinfo=ZoneInfo('Asia/Magadan'))),  # pay respect timezone in datetime
    (datetime(2022, 10, 10, 15, 10, tzinfo=timezone.utc), datetime(2022, 10, 10, 15, 10, tzinfo=timezone.utc)),  # pay respect UTC timezone
])
def test_desired_shipment_date(create, user, course, desired_shipment_date, saved_date):
    order = create(user=user, item=course, desired_shipment_date=desired_shipment_date)

    order.refresh_from_db()

    assert order.desired_shipment_date == saved_date


def test_raise_when_desired_shipment_date_could_not_be_converted_to_datetime(create, user, course):
    with pytest.raises(OrderCreatorException):
        create(user=user, item=course, desired_shipment_date='not a valid string datetime')
