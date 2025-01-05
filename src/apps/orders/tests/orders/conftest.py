from decimal import Decimal

import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def user(mixer):
    return mixer.blend("users.User", first_name="Авраам Соломонович", last_name="Пейзенгольц")


@pytest.fixture
def course(factory):
    return factory.course(
        name="Кройка и шитьё",
        full_name="Курс кройки и шитья",
        name_genitive="Кройки и шитья",
        price=100500,
    )


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
