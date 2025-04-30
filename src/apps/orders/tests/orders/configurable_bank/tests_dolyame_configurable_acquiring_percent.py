from decimal import Decimal

import pytest

from apps.banking.models import AcquiringPercent
from apps.orders.models import Order

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def dynamic_percent():
    return [
        AcquiringPercent.objects.create(slug="dolyame-small", percent=Decimal("3.5")),
        AcquiringPercent.objects.create(slug="dolyame-big", percent=Decimal("4.5")),
    ]


def test_default_percent(call_purchase):
    call_purchase(desired_bank="dolyame")
    order = Order.objects.last()

    assert order.acquiring_percent == Decimal("1.5")


def test_single_configured_percent(call_purchase):
    AcquiringPercent.objects.create(slug="dolyame", percent=Decimal("2.5"))

    call_purchase(desired_bank="dolyame")
    order = Order.objects.last()

    assert order.acquiring_percent == Decimal("2.5")


@pytest.mark.usefixtures("dynamic_percent")
def test_small_if_course_is_not_expensive(call_purchase):
    call_purchase(desired_bank="dolyame")
    order = Order.objects.last()

    assert order.acquiring_percent == Decimal("3.5")


@pytest.mark.usefixtures("dynamic_percent")
def test_big_if_course_is_expensive(call_purchase, course):
    course.update(price=300500)

    call_purchase(desired_bank="dolyame")
    order = Order.objects.last()

    assert order.acquiring_percent == Decimal("4.5")
