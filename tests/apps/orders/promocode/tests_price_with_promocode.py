import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("ten_percent_promocode"),
]


@pytest.fixture(autouse=True)
def _freeze_stripe_course(mocker):
    mocker.patch("apps.stripebank.bank.StripeBank.ue", 70)  # let it be forever :'(


@pytest.mark.parametrize(
    "code",
    [
        "TESTCODE",
        "testcode",
        "testcode ",
        " testcode",
    ],
)
def test(api, course, code):
    got = api.get(f"/api/v2/courses/{course.slug}/promocode/?promocode={code}")

    assert got["price"] == 90450
    assert got["formatted_price"] == "90 450"
    assert got["currency"] == "RUB"
    assert got["currency_symbol"] == "₽"


@pytest.mark.parametrize(
    ("bank", "expected_price", "expected_formatted_price", "expected_currency", "expected_currency_symbol"),
    [
        ("tinkoff_bank", 90450, "90 450", "RUB", "₽"),
        ("tinkoff_credit", 90450, "90 450", "RUB", "₽"),
        ("stripe", 1292, "1 292", "EUR", "€"),
    ],
)
def test_promocode_with_bank(api, course, bank, expected_price, expected_formatted_price, expected_currency, expected_currency_symbol):
    got = api.get(f"/api/v2/courses/{course.slug}/promocode/?promocode=TESTCODE&desired_bank={bank}")

    assert got["price"] == expected_price
    assert got["formatted_price"] == expected_formatted_price
    assert got["currency"] == expected_currency
    assert got["currency_symbol"] == expected_currency_symbol


@pytest.mark.parametrize(
    "code",
    [
        "EV1L",
        "",
    ],
)
def test_bad_promocode(api, course, code):
    got = api.get(f"/api/v2/courses/{course.slug}/promocode/?promocode={code}")

    assert got["price"] == 100500


def test_incompatible_promocode(api, course, another_course, ten_percent_promocode):
    ten_percent_promocode.courses.add(course)

    got = api.get(f"/api/v2/courses/{another_course.slug}/promocode/?promocode=TESTCODE")

    assert got["price"] == 100500


def test_compatible_promocode(api, course, ten_percent_promocode):
    ten_percent_promocode.courses.add(course)

    got = api.get(f"/api/v2/courses/{course.slug}/promocode/?promocode=TESTCODE")

    assert got["price"] == 90450


def test_wihtout_promocode(api, course):
    got = api.get(
        f"/api/v2/courses/{course.slug}/promocode/",
    )

    assert got["price"] == 100500
    assert got["formatted_price"] == "100 500"
    assert got["currency"] == "RUB"
    assert got["currency_symbol"] == "₽"
