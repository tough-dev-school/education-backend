import pytest

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
