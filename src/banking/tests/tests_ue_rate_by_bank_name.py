import pytest

from banking.price_calculator import ue_rate_by_bank_name

pytestmark = [pytest.mark.django_db]


@pytest.fixture(autouse=True)
def _mock_tinkoff_bank_ue_rate(mocker):
    mocker.patch('tinkoff.bank.TinkoffBank.ue', 11)


@pytest.fixture(autouse=True)
def _mock_stripe_bank_ue_ratae(mocker):
    mocker.patch('stripebank.bank.StripeBank.ue', 22)


@pytest.mark.parametrize(('bank_name', 'rate'), [
    ('tinkoff_bank', 11),
    ('stripe', 22),
])
def test(bank_name, rate):
    assert ue_rate_by_bank_name(bank_name) == rate


def test_nonexistant_bank_name():
    with pytest.raises(KeyError):
        ue_rate_by_bank_name('non-existant')


@pytest.mark.parametrize('bank_name', ['', None])
def test_default_bank(bank_name):
    assert ue_rate_by_bank_name(bank_name) == 11, 'Should be rate from tinkoff bank'
