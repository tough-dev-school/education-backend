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


def test_run_with_relevant_order(order, run_trigger):
    RecordFeedbackTrigger.run()

    run_trigger.assert_called_once_with(RecordFeedbackTrigger.name, order.pk)


def test_not_running_trigger_for_not_paid_orders(order, run_trigger):
    order.setattr_and_save('paid', None)
    RecordFeedbackTrigger.run()

    run_trigger.assert_not_called()


def test_not_running_trigger_for_old_orders(order, run_trigger, freezer):
    freezer.move_to('2032-12-10 15:30')
    RecordFeedbackTrigger.run()

    run_trigger.assert_not_called()


def test_not_running_trigger_for_orders_without_record(order, run_trigger):
    order.setattr_and_save('record', None)
    RecordFeedbackTrigger.run()

    run_trigger.assert_not_called()
