from datetime import datetime

import pytest

from triggers import tasks
from triggers.started_purchase import StartedPurchaseTrigger

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-04 15:30'),
]


@pytest.fixture
def condition(mocker):
    return mocker.patch.object(StartedPurchaseTrigger, 'condition')


@pytest.fixture
def run_trigger(mocker):
    return mocker.patch.object(tasks.run_trigger, 'delay')


def find_orders():
    return list(StartedPurchaseTrigger.find_orders())


def test_find_orders_with_relevant_order(order):
    assert find_orders() == [1]


def test_not_running_trigger_for_paid_orders(order):
    order.setattr_and_save('paid', datetime(2032, 12, 1, 15, 13))

    assert order.pk not in find_orders()


def test_not_running_trigger_for_old_orders(order, freezer):
    freezer.move_to('2032-12-10 15:30')

    assert order.pk not in find_orders()
