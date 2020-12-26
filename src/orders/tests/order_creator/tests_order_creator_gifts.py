from datetime import datetime

import pytest

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
        desired_shipment_date=datetime(2032, 12, 15),
        gift_message='Учись давай!',
    )

    assert order.giver == another_user
    assert order.desired_shipment_date == datetime(2032, 12, 15)
    assert order.gift_message == 'Учись давай!'
