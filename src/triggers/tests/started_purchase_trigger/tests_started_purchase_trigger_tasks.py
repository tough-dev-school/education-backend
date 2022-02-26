import pytest
from datetime import datetime

from triggers import tasks
from triggers.started_purchase import StartedPurchaseTrigger

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


@pytest.fixture
def condition(mocker):
    return mocker.patch.object(StartedPurchaseTrigger, 'condition')


@pytest.fixture
def run_trigger(mocker):
    return mocker.patch.object(tasks.run_started_purchase_trigger, 'delay')


def test_single_task_runs_the_trigger(condition, order):
    tasks.run_started_purchase_trigger.delay(order.pk)

    condition.assert_called_once()


def test_main_task(order, run_trigger):
    tasks.check_for_started_purchase_triggers()

    run_trigger.assert_called_once_with(order.pk)


def test_not_running_trigger_for_paid_orders(order, run_trigger):
    order.setattr_and_save('paid', datetime(2032, 12, 1, 15, 13))

    tasks.check_for_started_purchase_triggers()

    run_trigger.assert_not_called()


def test_not_running_trigger_for_shipped_orders(order, run_trigger):
    order.ship_without_payment()

    tasks.check_for_started_purchase_triggers()

    run_trigger.assert_not_called()


def test_not_running_trigger_for_old_orders(order, run_trigger, freezer):
    freezer.move_to('2038-12-01 15:30')  # far in the future

    tasks.check_for_started_purchase_triggers()

    run_trigger.assert_not_called()
