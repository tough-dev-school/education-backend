from decimal import Decimal

import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def promocode(mixer):
    return mixer.blend("orders.PromoCode", discount_percent=10, name="TESTCODE")


@pytest.fixture
def course(mixer):
    return mixer.blend("products.Course", price=100500)


@pytest.fixture(autouse=True)
def _freeze_currency_rates(mocker):
    mocker.patch("apps.stripebank.bank.StripeBankUSD.get_currency_rate", return_value=Decimal(70))  # let it be forever :'(
    mocker.patch("apps.stripebank.bank.StripeBankKZT.get_currency_rate", return_value=Decimal("0.18"))


@pytest.fixture
def draft(anon):
    """Create and fetch an order draft"""

    def _draft(slug: str, expected_status_code: int | None = 200, **kwargs: dict):
        return anon.post(
            "/api/v2/orders/draft/",
            {
                "course": slug,
                **kwargs,
            },
            expected_status_code=expected_status_code,
        )

    return _draft


def test_course_only(draft, course):
    got = draft(course.slug)

    assert got["course"]["name"] == course.name
    assert got["price"]["price"] == str(course.price)


@pytest.mark.parametrize(
    ("price", "expected", "formatted"),
    [
        (Decimal("200.51"), "200.51", "200,51"),
        (100500, "100500", "100\xa0500"),
    ],
)
def test_price(draft, course, price, expected, formatted):
    course.update(price=price)

    got = draft(course.slug)

    assert got["price"]["price"] == expected
    assert got["price"]["formatted_price"] == formatted
    assert got["price"]["currency"] == "RUB"
    assert got["price"]["currency_symbol"] == "₽"


def test_invalid_course_slug(draft):
    draft("nonexsitant-course-slug", expected_status_code=400)


@pytest.mark.parametrize(
    "code",
    [
        "TESTCODE",
        "testcode",
        "testcode ",
        " testcode",
    ],
)
def test_promocode(draft, course, code):
    got = draft(course.slug, promocode=code)

    assert got["price"]["price"] == "90450"


def test_bad_promocode(draft, course):
    got = draft(course.slug, promocode="EV1L")

    assert got["price"]["price"] == "100500"


@pytest.mark.parametrize("nothing", ["", None])
def test_empty_promocode(draft, course, nothing):
    draft(course.slug, promocode=nothing, expected_status_code=400)


@pytest.mark.parametrize(
    ("bank", "expected_price", "expected_formatted_price", "expected_currency", "expected_currency_symbol"),
    [
        ("tinkoff_bank", "90450", "90 450", "RUB", "₽"),
        ("stripe", "1292", "1 292", "USD", "$"),
        ("stripe_kz", "502500", "502 500", "KZT", "₸"),
    ],
)
def test_promocode_with_bank(draft, course, bank, expected_price, expected_formatted_price, expected_currency, expected_currency_symbol):
    got = draft(course.slug, promocode="TESTCODE", desired_bank=bank)

    assert got["price"]["price"] == expected_price
    assert got["price"]["formatted_price"] == expected_formatted_price
    assert got["price"]["currency"] == expected_currency
    assert got["price"]["currency_symbol"] == expected_currency_symbol


def test_bad_bank(draft, course):
    draft(course.slug, desired_bank="EV1L", expected_status_code=400)
