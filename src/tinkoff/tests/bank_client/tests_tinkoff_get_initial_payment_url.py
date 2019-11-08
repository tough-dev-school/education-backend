import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def req(mocker):
    yield mocker.patch('tinkoff.client.TinkoffBank.call', return_value={
        'PaymentURL': 'https://mocked.in.fixture/',
    })


def test_ok_initial_payment_url(tinkoff):
    tinkoff.m.post('https://securepay.tinkoff.ru/v2/Init/', json={
        'Success': True,
        'PaymentURL': 'https://pay.ment/url',
    })

    assert tinkoff.get_initial_payment_url() == 'https://pay.ment/url'


def test_initial_payment_url_payload(tinkoff, req, settings):
    assert tinkoff.get_initial_payment_url() == 'https://mocked.in.fixture/'

    payload = req.call_args[1]['payload']

    assert payload['OrderId'] == tinkoff.order.id
    assert payload['CustomerKey'] == tinkoff.order.user.id

    assert settings.FRONTEND_URL in payload['SuccessURL']
    assert settings.FRONTEND_URL in payload['FailURL']

    assert 'Receipt' in payload
