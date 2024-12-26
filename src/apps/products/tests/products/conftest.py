from decimal import Decimal

import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def testcode(mixer):
    return mixer.blend("orders.PromoCode", name="TESTCODE", discount_percent=10)


@pytest.fixture
def default_user_data():
    """Data used during purchase tests. Shortcut just to save typing time"""
    return {
        "name": "Забой Шахтёров",
        "email": "zaboy@gmail.com",
    }


@pytest.fixture(autouse=True)
def _create_currency_rates(factory):
    factory.currency_rate(name="RUB", rate=1)
    factory.currency_rate(name="USD", rate=70)
    factory.currency_rate(name="KZT", rate=Decimal("0.18"))
    factory.currency_rate(name="KIS", rate=1)


@pytest.fixture(autouse=True)
def _create_acquiring_percents(factory):
    factory.acquiring(bank="tinkoff_bank", percent=Decimal("2.79"))
    factory.acquiring(bank="stripe", percent=Decimal(4))
    factory.acquiring(bank="stripe_kz", percent=Decimal(4))
    factory.acquiring(bank="dolyame", percent=Decimal("6.9"))
    factory.acquiring(bank="zero_price", percent=Decimal(0))
