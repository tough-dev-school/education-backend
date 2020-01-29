import pytest

from triggers.tasks import run_all_triggers, run_trigger

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def get_all_triggers_result(mocker):
    return mocker.patch('triggers.factory.get_all_triggers')


@pytest.fixture
def trigger_run_result(mocker, test_trigger):
    return mocker.patch.object(test_trigger, 'run')


@pytest.fixture
def trigger_execute_result(mocker, test_trigger):
    return mocker.patch.object(test_trigger, '__call__')


def test_runner_all_triggers_task(get_all_triggers_result, trigger_run_result, test_trigger):
    get_all_triggers_result.return_value = [test_trigger]
    run_all_triggers()

    trigger_run_result.assert_called_once()


def test_run_trigger_task(order, test_trigger, trigger_execute_result):
    run_trigger.delay(test_trigger.name, order.pk)

    trigger_execute_result.assert_called_once()
