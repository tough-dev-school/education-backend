import pytest

from apps.mailing.configuration import get_configuration
from apps.orders.models import Order

pytestmark = [pytest.mark.django_db]


def test_user_without_purchases_has_no_configuration(user):
    assert get_configuration(recipient=user.email) is None


@pytest.mark.parametrize("is_order_paid", [True, False])
def test_course_with_configuration(factory, configuration, user, is_order_paid):
    factory.order(user=user, item=configuration.course, is_paid=is_order_paid)

    assert get_configuration(recipient=user.email) == configuration


@pytest.mark.parametrize("is_order_paid", [True, False])
def test_last_course_contains_no_configuration(factory, course, user, is_order_paid):
    factory.order(user=user, item=course, is_paid=is_order_paid)

    assert get_configuration(recipient=user.email) is None


def test_orders_without_itema_do_not_break_things(factory, configuration, user):
    factory.order(user=user, item=configuration.course)
    factory.order(user=user).update(course=None)

    assert get_configuration(recipient=user.email) == configuration


def test_courses_are_ordered_by_creation_1(factory, configuration, another_configuration, user):
    order1 = factory.order(user=user, item=another_configuration.course)
    order2 = factory.order(user=user, item=configuration.course)

    Order.objects.filter(pk=order1.pk).update(created="2032-12-01 16:20+04:00")
    Order.objects.filter(pk=order2.pk).update(created="2032-12-01 15:30+04:00")

    assert get_configuration(recipient=user.email) == another_configuration


def test_courses_are_ordered_by_creation_2(factory, configuration, another_configuration, user):
    order1 = factory.order(user=user, item=another_configuration.course)
    order2 = factory.order(user=user, item=configuration.course)

    Order.objects.filter(pk=order2.pk).update(created="2032-12-01 16:20+04:00")
    Order.objects.filter(pk=order1.pk).update(created="2032-12-01 15:30+04:00")

    assert get_configuration(recipient=user.email) == configuration
