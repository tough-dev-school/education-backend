import pytest
from datetime import datetime, timezone

from triggers.record_feedback import RecordFeedbackTrigger

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def order(order, record):
    order.set_item(record)
    order.setattr_and_save('paid', datetime(2032, 12, 1, 15, 13, tzinfo=timezone.utc))

    return order


@pytest.fixture
def trigger(order):
    return RecordFeedbackTrigger(order)
