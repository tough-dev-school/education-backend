import pytest
from datetime import datetime

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


@pytest.fixture
def order(factory):
    return factory.order(bank_id='dolyame')


@pytest.fixture(autouse=True)
def _disable_dolyame_authn(mocker):
    mocker.patch('tinkoff.api.permissions.DolyameNetmaskPermission.has_permission', return_value=True)


@pytest.fixture(autouse=True)
def atol_receipt_printer(mocker):
    mocker.patch('banking.tasks.AtolClient.__call__')
    return mocker.patch('banking.tasks.AtolClient.__init__', return_value=None)


@pytest.fixture
def notification(order):
    def _notification(status: str, **kwargs):
        return {
            'id': order.slug,
            'status': status,
            'amount': 10000.56,
            'residual_amount': 7500.42,
            'demo': False,
            'client_info': {
                'first_name': 'Иван',
                'last_name': 'И.',
                'middle_name': 'Иванович',
                'email': 't**@y*.ru',
                'phone': '+79003332211',
                'birthdate': '1997-05-15',
            },
            **kwargs,
        }

    return _notification


def test_ok(api, order, notification):
    api.post('/api/v2/banking/dolyame-notifications/', notification(
        status='completed',
    ), expected_status_code=200)

    order.refresh_from_db()

    assert order.paid == datetime(2032, 12, 1, 15, 30)


def test_atol_receipt_is_printed(api, order, notification, atol_receipt_printer):
    api.post('/api/v2/banking/dolyame-notifications/', notification(
        status='completed',
    ), expected_status_code=200)

    order.refresh_from_db()

    atol_receipt_printer.assert_called_once_with(order=order)


@pytest.mark.parametrize('status', ['approved', 'rejected'])
def test_wr0ng_status(api, order, notification, status):
    api.post('/api/v2/banking/dolyame-notifications/', notification(
        status=status,
    ), expected_status_code=200)

    order.refresh_from_db()

    assert order.paid is None
