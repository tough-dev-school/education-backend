import pytest

from orders.models import Order

pytestmark = [pytest.mark.django_db]


def test_tinkoff_bank_is_called_by_default(call_purchase, tinkoff_bank, tinkoff_credit):
    call_purchase()

    tinkoff_bank.assert_called_once()
    tinkoff_credit.assert_not_called()


def test_tinkoff_bank(call_purchase, tinkoff_bank, tinkoff_credit):
    call_purchase(desired_bank='tinkoff_bank')

    tinkoff_bank.assert_called_once()
    tinkoff_credit.assert_not_called()


def test_tinkoff_credit(call_purchase, tinkoff_bank, tinkoff_credit):
    call_purchase(desired_bank='tinkoff_credit')

    tinkoff_bank.assert_not_called()
    tinkoff_credit.assert_called_once()


def test_stripe_bank(call_purchase, tinkoff_bank, stripe_bank):
    call_purchase(desired_bank='stripe')

    tinkoff_bank.assert_not_called()
    stripe_bank.assert_called_once()


@pytest.mark.parametrize('bank', ['tinkoff_credit', 'stripe', 'tinkoff_bank'])
def test_desired_bank_is_saved(call_purchase, bank):
    call_purchase(desired_bank=bank)

    order = Order.objects.last()

    assert order.desired_bank == bank


def test_by_default_desired_bank_is_empty_string(call_purchase):
    call_purchase()

    order = Order.objects.last()

    assert order.desired_bank == ''


def test_desired_bank_is_stored_during_gift(api, default_gift_data):
    api.post(
        '/api/v2/courses/ruloning-oboev/gift/',
        {
            **default_gift_data,
            'desired_bank': 'tinkoff_credit',
        },
        format='multipart', expected_status_code=302)

    order = Order.objects.last()

    assert order.desired_bank == 'tinkoff_credit'
