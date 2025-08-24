from decimal import Decimal

import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def course(factory):
    return factory.course(price=90450)


@pytest.fixture(autouse=True)
def group(mixer, course):
    group = mixer.blend("products.Group", slug="rolling-in-it")

    course.update(group=group)


@pytest.fixture(autouse=True)
def _freeze_currency_rates(mocker):
    mocker.patch("apps.stripebank.bank.StripeBankUSD.get_currency_rate", return_value=Decimal(70))
    mocker.patch("apps.stripebank.bank.StripeBankKZT.get_currency_rate", return_value=Decimal("0.18"))


def test_list(anon, course):
    got = anon.get("/api/v2/course-groups/rolling-in-it/courses/")

    assert got[0]["slug"] == course.slug
    assert got[0]["name"] == course.name
    assert got[0]["price"]["price"] == "90450"
    assert got[0]["price"]["formatted_price"] == "90\xa0450"


def test_404_for_nonexistant_slug(anon):
    anon.get("/api/v2/course-groups/nonexistant/courses/", expected_status_code=404)


def test_another_groups_are_excluded(anon, course, mixer):
    course.update(group=mixer.blend("products.Group"))

    got = anon.get("/api/v2/course-groups/rolling-in-it/courses/")

    assert len(got) == 0


@pytest.mark.parametrize(
    ("bank", "expected_price", "expected_formatted_price", "expected_currency", "expected_currency_symbol"),
    [
        ("tinkoff_bank", "90450", "90\xa0450", "RUB", "₽"),
        ("stripe", "1292", "1\xa0292", "USD", "$"),
        ("stripe_kz", "502500", "502\xa0500", "KZT", "₸"),
    ],
)
def test_price_by_bank(anon, bank, expected_price, expected_formatted_price, expected_currency, expected_currency_symbol):
    got = anon.get(f"/api/v2/course-groups/rolling-in-it/courses/?desired_bank={bank}")

    assert got[0]["price"]["price"] == expected_price
    assert got[0]["price"]["formatted_price"] == expected_formatted_price
    assert got[0]["price"]["currency"] == expected_currency
    assert got[0]["price"]["currency_symbol"] == expected_currency_symbol
