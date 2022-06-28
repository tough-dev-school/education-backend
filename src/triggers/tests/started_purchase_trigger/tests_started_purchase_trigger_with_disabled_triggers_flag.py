import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


def test_sent_by_default(trigger, freezer):
    freezer.move_to('2032-12-02 16:00')

    assert trigger.should_be_sent() is True


@pytest.mark.parametrize('disable_triggers', [True, False])
def test_not_sent_if_order_has_a_giver(trigger, freezer, disable_triggers):
    freezer.move_to('2032-12-02 16:00')

    trigger.order.course.setattr_and_save('disable_triggers', disable_triggers)

    assert trigger.should_be_sent() is not disable_triggers
