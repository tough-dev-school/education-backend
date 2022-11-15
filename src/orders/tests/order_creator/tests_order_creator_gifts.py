import pytest
from datetime import datetime, timedelta, timezone
from django.conf import settings
from zoneinfo import ZoneInfo

from orders.services.order_creator import OrderCreatorException

pytestmark = [pytest.mark.django_db]


def test_no_gifts_by_default(create, user, course):
    order = create(user=user, item=course)

    assert order.giver is None
    assert order.desired_shipment_date is None
    assert order.gift_message == ''


def test_fields(create, user, another_user, course):
    order = create(
        user=user,
        item=course,
        giver=another_user,
        desired_shipment_date=datetime(2032, 12, 15, tzinfo=ZoneInfo('Asia/Magadan')),
        gift_message='Учись давай!',
    )

    assert order.user == user  # order receiver
    assert order.giver == another_user  # the one, who had created the gift
    assert order.desired_shipment_date == datetime(2032, 12, 15, tzinfo=ZoneInfo('Asia/Magadan'))
    assert order.gift_message == 'Учись давай!'


@pytest.mark.parametrize(('desired_shipment_date', 'saved_date'), [
    (
        None,
        None,  # empty desired_shipment_date
    ),
    (
        '2022-10-10 12:40',
        datetime(2022, 10, 10, 12, 40, tzinfo=ZoneInfo(settings.TIME_ZONE)),  # string without timezone saved as datetime with default timezone
    ),
    (
        '2022-10-10 12:40-12:00',
        datetime(2022, 10, 10, 12, 40, tzinfo=timezone(timedelta(hours=-12))),  # pay respect to negative timezone
    ),
    (
        '2022-10-10 12:40Z',
        datetime(2022, 10, 10, 12, 40, tzinfo=timezone.utc),  # pay respect to UTC timezone passed as `Z`
    ),
    (
        datetime(2022, 10, 10, 15, 10),
        datetime(2022, 10, 10, 15, 10, tzinfo=ZoneInfo(settings.TIME_ZONE)),  # datetime without timezone saved with default timezone
    ),
])
def test_desired_shipment_date(create, user, course, desired_shipment_date, saved_date):
    order = create(user=user, item=course, desired_shipment_date=desired_shipment_date)

    order.refresh_from_db()

    assert order.desired_shipment_date == saved_date


def test_raise_when_desired_shipment_date_could_not_be_converted_to_datetime(create, user, course):
    with pytest.raises(OrderCreatorException, match='is not ISO formatted'):
        create(user=user, item=course, desired_shipment_date='not a valid string datetime')
