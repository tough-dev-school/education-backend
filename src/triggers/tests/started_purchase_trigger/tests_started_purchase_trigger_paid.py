import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


@pytest.mark.parametrize('change_order, should_be_sent', [
    [lambda order: None, True],
    [lambda order: order.set_paid(), False],
])
def test(trigger, change_order, should_be_sent, freezer):
    freezer.move_to('2032-12-02 16:00')
    change_order(trigger.order)

    assert trigger.should_be_sent() is should_be_sent
