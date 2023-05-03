import pytest

from triggers import tasks
from triggers.record_feedback import RecordFeedbackTrigger

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-01 15:30"),
]


@pytest.fixture
def condition(mocker):
    return mocker.patch.object(RecordFeedbackTrigger, "condition")


@pytest.fixture
def run_trigger(mocker):
    return mocker.patch.object(tasks.run_record_feedback_trigger, "delay")


def test_single_task_runs_the_trigger(condition, order):
    tasks.run_record_feedback_trigger.delay(order.pk)

    condition.assert_called_once()


def test_main_task(order, run_trigger):
    tasks.check_for_record_feedback_triggers()

    run_trigger.assert_called_once_with(order.pk)


def test_not_running_trigger_for_not_paid_orders(order, run_trigger):
    order.setattr_and_save("paid", None)
    tasks.check_for_record_feedback_triggers()

    run_trigger.assert_not_called()


def test_not_running_trigger_for_old_orders(order, run_trigger, freezer):
    freezer.move_to("2038-12-01 15:30")  # far in the future

    tasks.check_for_record_feedback_triggers()

    run_trigger.assert_not_called()


def test_not_running_trigger_for_orders_without_record(order, run_trigger):
    order.setattr_and_save("record", None)

    tasks.check_for_record_feedback_triggers()

    run_trigger.assert_not_called()
