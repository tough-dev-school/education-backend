import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-01 15:30"),
]


def test_sent_by_default(trigger, freezer):
    freezer.move_to("2032-12-02 16:00")

    assert trigger.should_be_sent() is True


def test_not_sent_if_order_has_a_giver(trigger, freezer, another_user):
    freezer.move_to("2032-12-02 16:00")

    trigger.order.giver = another_user

    assert trigger.should_be_sent() is False
