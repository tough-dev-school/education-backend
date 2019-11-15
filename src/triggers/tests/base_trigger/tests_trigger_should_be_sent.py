import pytest

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def another_order(mixer):
    return mixer.blend('orders.Order')


def test_is_sent(test_trigger, mixer, order):
    mixer.blend('triggers.TriggerLogEntry', order=order, trigger='test')

    assert test_trigger(order).should_be_sent() is False


def test_another_order(test_trigger, mixer, order, another_order):
    mixer.blend('triggers.TriggerLogEntry', order=another_order, trigger='test')

    assert test_trigger(order).should_be_sent() is True


def test_another_order_with_the_same_email(test_trigger, mixer, order, another_order):
    mixer.blend('triggers.TriggerLogEntry', order=another_order, trigger='test')

    another_order.user.email = order.user.email
    another_order.user.save()

    assert test_trigger(order).should_be_sent() is False


def test_another_trigger(test_trigger, mixer, order):
    mixer.blend('triggers.TriggerLogEntry', order=order, trigger='another-name-that-does-not-exist')

    assert test_trigger(order).should_be_sent() is True


@pytest.mark.parametrize('condition', [True, False])
def test_condition(test_trigger, mixer, order, mocker, condition):
    mocker.patch.object(test_trigger, 'condition', return_value=condition)

    assert test_trigger(order).should_be_sent() is condition
