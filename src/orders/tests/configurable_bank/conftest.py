import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def course(mixer):
    return mixer.blend('products.Course', slug='ruloning-oboev', price=1900)


@pytest.fixture
def default_user_data():
    return {
        'name': 'Забой Шахтёров',
        'email': 'zaboy@gmail.com',
    }


@pytest.fixture
def default_gift_data():
    return {
        'receiver_name': 'Забой Шахтёров',
        'receiver_email': 'zaboy@gmail.com',
        'giver_name': 'Камаз Помоев',
        'giver_email': 'kamaz@gmail.com',
        'desired_shipment_date': '2032-12-01 12:35:15',
    }


@pytest.fixture
def call_purchase(api, default_user_data):
    return lambda **kwargs: api.post(
        '/api/v2/courses/ruloning-oboev/purchase/',
        {
            **default_user_data,
            **kwargs,
        },
        format='multipart', expected_status_code=302,
    )


@pytest.fixture(autouse=True)
def tinkoff_bank(mocker):
    return mocker.patch('tinkoff.bank.TinkoffBank.get_initial_payment_url', return_value='https://mocked.link')


@pytest.fixture(autouse=True)
def tinkoff_credit(mocker):
    return mocker.patch('tinkoff.credit.TinkoffCredit.get_initial_payment_url', return_value='https://mocked.link')


@pytest.fixture(autouse=True)
def stripe_bank(mocker):
    return mocker.patch('stripebank.bank.StripeBank.get_initial_payment_url', return_value='https://mocked.link')


@pytest.fixture(autouse=True)
def _freeze_ue_rate(mocker):
    mocker.patch('tinkoff.bank.TinkoffBank.ue', 11)
    mocker.patch('tinkoff.credit.TinkoffCredit.ue', 22)
    mocker.patch('stripebank.bank.StripeBank.ue', 33)
