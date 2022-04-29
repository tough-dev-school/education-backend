import pytest
from decimal import Decimal

from tinkoff.models import DolyameNotification

pytestmark = [pytest.mark.django_db]


def test_data(api, notification, payment_schedule):
    api.post('/api/v2/banking/dolyame-notifications/', notification(status='approved', payment_schedule=payment_schedule), expected_status_code=200)

    notification = DolyameNotification.objects.last()

    assert notification.status == 'approved'
    assert notification.order_id == 100500
    assert notification.amount == Decimal('10000.56')
    assert notification.residual_amount == Decimal('7500.42')
    assert notification.demo is False
    assert notification.client_info['first_name'] == 'Иван'
    assert notification.client_info['last_name'] == 'И.'
    assert notification.client_info['phone'] == '+79003332211'
    assert notification.payment_schedule[0]['payment_date'] == '2020-11-20'
    assert notification.payment_schedule[0]['amount'] == 2500.14
    assert notification.payment_schedule[0]['status'] == 'hold'


@pytest.mark.parametrize('status', ['rejected', 'canceled', 'commited'])
def test_status(api, notification, status):
    api.post('/api/v2/banking/dolyame-notifications/', notification(status=status), expected_status_code=200)

    notification = DolyameNotification.objects.last()

    assert notification.status == status


def test_permission(fake_client, notification):
    fake_client.post('/api/v2/banking/dolyame-notifications/', notification(status='approved'), expected_status_code=401)

    assert not DolyameNotification.objects.exists()
