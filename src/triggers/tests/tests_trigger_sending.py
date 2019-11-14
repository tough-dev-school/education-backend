import pytest

from triggers.models import TriggerLogEntry

pytestmark = [pytest.mark.django_db]


def pytest_generate_tests(metafunc):
    metafunc.parametrize('condition', [True, False])


def log_entry(order):
    return TriggerLogEntry.objects.filter(order=order, trigger='test')


@pytest.fixture(autouse=True)
def send(test_trigger, mocker):
    return mocker.patch.object(test_trigger, 'send')


def test_send_is_called(mocker, test_trigger, order, send, condition):
    mocker.patch.object(test_trigger, 'condition', return_value=condition)

    test_trigger(order)()

    assert (send.call_count == 1) is condition


def test_log(mocker, test_trigger, order, condition):
    mocker.patch.object(test_trigger, 'condition', return_value=condition)

    test_trigger(order)()

    assert log_entry(order).exists() is condition


def test_log_on_successfull_send(send, test_trigger, order, condition):
    sent_was_ok = condition
    send.return_value = sent_was_ok

    test_trigger(order)()

    assert log_entry(order).exists() is condition
