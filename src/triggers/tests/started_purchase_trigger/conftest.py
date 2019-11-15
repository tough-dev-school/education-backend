import pytest

from triggers.started_purchase import StartedPurchaseTrigger

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def trigger(order):
    return StartedPurchaseTrigger(order)
