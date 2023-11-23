import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def course(factory):
    return factory.course(slug="ruloning-oboev", price=1900)


@pytest.fixture
def default_user_data():
    return {
        "name": "Забой Шахтёров",
        "email": "zaboy@gmail.com",
    }


@pytest.fixture
def call_purchase(api, default_user_data):
    return lambda as_response=False, **kwargs: api.post(
        "/api/v2/courses/ruloning-oboev/purchase/",
        {
            **default_user_data,
            **kwargs,
        },
        format="multipart",
        expected_status_code=302,
        as_response=as_response,
    )


@pytest.fixture(autouse=True)
def tinkoff_bank(mocker):
    return mocker.patch("apps.tinkoff.bank.TinkoffBank.get_initial_payment_url", return_value="https://mocked.link")


@pytest.fixture(autouse=True)
def stripe_bank(mocker):
    return mocker.patch("apps.stripebank.bank.StripeBank.get_initial_payment_url", return_value="https://mocked.link")


@pytest.fixture(autouse=True)
def dolyame_bank(mocker):
    return mocker.patch("apps.tinkoff.dolyame.Dolyame.get_initial_payment_url", return_value="https://mocked.link")


@pytest.fixture(autouse=True)
def _freeze_ue_rate(mocker):
    mocker.patch("apps.tinkoff.bank.TinkoffBank.ue", 11)
    mocker.patch("apps.stripebank.bank.StripeBank.ue", 33)
    mocker.patch("apps.tinkoff.dolyame.Dolyame.ue", 44)


@pytest.fixture(autouse=True)
def _freeze_acquiring_percent(mocker):
    mocker.patch("apps.tinkoff.bank.TinkoffBank.acquiring_percent", "1.2")
    mocker.patch("apps.stripebank.bank.StripeBank.acquiring_percent", "1.4")
    mocker.patch("apps.tinkoff.dolyame.Dolyame.acquiring_percent", "1.5")
