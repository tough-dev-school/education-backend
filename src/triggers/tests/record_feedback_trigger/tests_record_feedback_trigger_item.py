import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-01 15:30"),
]


def test_conditions_for_order_with_record(trigger, freezer):
    freezer.move_to("2032-12-04 16:00")

    assert trigger.should_be_sent() is True


def test_conditions_for_order_with_course(trigger, freezer, course):
    freezer.move_to("2032-12-04 16:00")
    trigger.order.set_item(course)
    trigger.order.save()

    assert trigger.should_be_sent() is False


def test_conditions_for_order_with_bundle(trigger, freezer, bundle):
    freezer.move_to("2032-12-04 16:00")
    trigger.order.set_item(bundle)
    trigger.order.save()

    assert trigger.should_be_sent() is False
