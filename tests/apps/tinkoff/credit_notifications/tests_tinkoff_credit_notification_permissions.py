import pytest

from core.test.api_client import DRFClient
from apps.tinkoff.models import CreditNotification

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def fake_client():
    return DRFClient(anon=True, HTTP_X_FORWARDED_FOR="8.8.8.8, 10.0.0.1")


def test(fake_client, notification):
    fake_client.post("/api/v2/banking/tinkoff-credit-notifications/", notification, expected_status_code=401)

    assert not CreditNotification.objects.exists()
