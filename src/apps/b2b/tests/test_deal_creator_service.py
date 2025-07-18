from decimal import Decimal

import pytest

from apps.b2b.services import DealCreator

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("_set_current_user"),
]


@pytest.fixture(autouse=True)
def _kzt(factory):
    factory.currency(name="KZT", rate=Decimal("0.2"))


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


@pytest.mark.parametrize(
    ("currency", "expected_rate"),
    [
        ("RUB", "1.0"),
        ("NNE", "1.0"),  # unknown currency
        ("KZT", "0.2"),
    ],
)
def test_currency_is_saved(customer, course, currency, expected_rate):
    deal = DealCreator(
        customer=customer,
        course=course,
        price=Decimal("100.50"),
        currency=currency,
    )()

    assert deal.currency == currency
    assert deal.currency_rate_on_creation == Decimal(expected_rate)
