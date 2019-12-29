import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time('2032-12-01 15:30'),
]


def test_conditions_for_order_with_record(trigger, freezer):
    freezer.move_to('2032-12-04 16:00')

    assert trigger.should_be_sent() is True


def test_conditions_for_order_with_course(trigger, freezer, course, order):
    freezer.move_to('2032-12-04 16:00')
    order.set_item(course)

    assert trigger.should_be_sent() is False


def test_conditions_for_order_with_bundle(trigger, freezer, bundle, order):
    freezer.move_to('2032-12-04 16:00')
    order.set_item(bundle)

    assert trigger.should_be_sent() is False
