import pytest

from apps.orders.models import PromoCode

pytestmark = [pytest.mark.django_db]


@pytest.mark.parametrize(
    "name",
    [
        "TESTCODE",
        "testcode",
        "tEStCOde",
        "  TESTCODE",
        "TESTCODE  ",
    ],
)
def test_found(ten_percent_promocode, name):
    assert PromoCode.objects.get_or_nothing(name=name) == ten_percent_promocode


@pytest.mark.usefixtures("ten_percent_promocode")
def test_not_found():
    assert PromoCode.objects.get_or_nothing(name="NONEXISTANT") is None


def test_not_found_when_promo_code_is_disabled(ten_percent_promocode):
    ten_percent_promocode.update(active=False)

    assert PromoCode.objects.get_or_nothing(name="TESTCODE") is None


@pytest.mark.freeze_time("2032-12-01 15:30:00+04:00")
@pytest.mark.parametrize(
    ("expires", "is_found"),
    [
        ("2032-12-01 15:30:00+04:00", True),
        ("2032-11-10 15:30:00+04:00", False),
        ("2032-12-05 15:30:00+04:00", True),
    ],
)
def test_not_found_when_promo_code_has_expired(ten_percent_promocode, expires, is_found):
    ten_percent_promocode.update(expires=expires)

    assert (PromoCode.objects.get_or_nothing(name="TESTCODE") is not None) is is_found


@pytest.mark.usefixtures("ten_percent_promocode")
def test_empty_name():
    assert PromoCode.objects.get_or_nothing(name=None) is None
