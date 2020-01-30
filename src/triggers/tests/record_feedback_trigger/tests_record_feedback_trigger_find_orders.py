import pytest

from triggers import tasks
from triggers.record_feedback import RecordFeedbackTrigger

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-04 15:30'),
]


@pytest.fixture
def condition(mocker):
    return mocker.patch.object(RecordFeedbackTrigger, 'condition')


@pytest.fixture
def run_trigger(mocker):
    return mocker.patch.object(tasks.run_trigger, 'delay')


def test_find_orders_with_relevant_order(order):
    orders = list(RecordFeedbackTrigger.find_orders())

    assert orders == [1]


def test_not_running_trigger_for_not_paid_orders(order):
    order.setattr_and_save('paid', None)
    orders = list(RecordFeedbackTrigger.find_orders())

    assert orders == []


def test_not_running_trigger_for_old_orders(order, freezer):
    freezer.move_to('2032-12-10 15:30')
    orders = list(RecordFeedbackTrigger.find_orders())

    assert orders == []


def test_not_running_trigger_for_orders_without_record(order):
    order.setattr_and_save('record', None)
    orders = list(RecordFeedbackTrigger.find_orders())

    assert orders == []
