import pytest

from triggers.tasks import run_all_triggers, run_trigger

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def get_all_triggers_result(mocker):
    return mocker.patch('triggers.factory.get_all_triggers')


@pytest.fixture
def find_orders(mocker, test_trigger):
    return mocker.patch.object(test_trigger, 'find_orders')


@pytest.fixture
def trigger_task(mocker):
    return mocker.patch('triggers.tasks.run_trigger.delay')


@pytest.fixture
def execute_result(mocker, test_trigger):
    return mocker.patch.object(test_trigger, '__call__')


def test_runner_all_triggers_task(get_all_triggers_result, find_orders, test_trigger, trigger_task, order):
    get_all_triggers_result.return_value = [test_trigger]
    find_orders.return_value = [order.pk]
    run_all_triggers()

    find_orders.assert_called_once()
    trigger_task.assert_called_once_with('test', order.pk)


def test_run_trigger_task(order, test_trigger, execute_result):
    run_trigger.delay(test_trigger.name, order.pk)

    execute_result.assert_called_once()
