import pytest
from datetime import datetime

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


@pytest.fixture(autouse=True)
def _disable_tinkoff_authn(mocker):
    mocker.patch('tinkoff.api.permissions.TinkoffCreditNetmaskPermission.has_permission', return_value=True)


@pytest.fixture
def bank_data():
    def _bank_data(**kwargs):
        return {
            'created_at': '2021-02-06T13:08:02.845Z',
            'committed': False,
            'first_payment': 0,
            'order_amount': 5200,
            'credit_amount': 5200,
            'product': 'credit',
            'term': 6,
            'monthly_payment': 944.32,
            'first_name': 'Удой',
            'last_name': 'Коровов',
            'middle_name': None,
            'phone': '+79031234567',
            'loan_number': None,
            'email': 'konstantin13@ip.biz',
            **kwargs,
        }
    return _bank_data


def test_ok(api, order, bank_data):
    api.post('/api/v2/banking/tinkoff-credit-notifications/', bank_data(
        status='signed',
        id=order.id,
    ), expected_status_code=200)

    order.refresh_from_db()

    assert order.paid == datetime(2032, 12, 1, 15, 30)


@pytest.mark.parametrize('status', ['approved', 'rejected'])
def test_wr0ng_status(api, order, bank_data, status):
    api.post('/api/v2/banking/tinkoff-credit-notifications/', bank_data(
        status=status,
        id=order.id,
    ), expected_status_code=200)

    order.refresh_from_db()

    assert order.paid is None
