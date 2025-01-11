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
def rub(factory):
    return factory.currency_rate(name="RUB", rate=1)


@pytest.fixture(autouse=True)
def usd(factory):
    return factory.currency_rate(name="USD", rate=70)


@pytest.fixture(autouse=True)
def kzt(factory):
    return factory.currency_rate(name="KZT", rate=Decimal("0.18"))


@pytest.fixture(autouse=True)
def kis(factory):
    return factory.currency_rate(name="KIS", rate=1)
