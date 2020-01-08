import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


@pytest.mark.parametrize('change_order, should_be_sent', [
    [lambda order: order.setattr_and_save('paid', None), False],
    [lambda order: order.set_paid(), True],
])
def test(trigger, change_order, should_be_sent, freezer):
    freezer.move_to('2032-12-04 16:00')
    change_order(trigger.order)

    assert trigger.should_be_sent() is should_be_sent
