import pytest

from app.test.api_client import DRFClient

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def notification(order):
    return {
        'id': order.slug,
        'status': 'approved',
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
    }


@pytest.fixture
def api():
    return DRFClient(anon=True, HTTP_X_FORWARDED_FOR='91.194.226.100, 10.0.0.1')
