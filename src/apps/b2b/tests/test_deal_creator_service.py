from decimal import Decimal

import pytest

from apps.b2b.services import DealCreator

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("_set_current_user"),
]


def test_deal_is_created(customer, course):
    deal = DealCreator(
        customer=customer,
        course=course,
        price=Decimal("100.50"),
        currency="RUB",
    )()

    assert deal.customer == customer
    assert deal.course == course
    assert str(deal.price) == "100.50"
    assert deal.author is not None, "Author is assigned during creation"
