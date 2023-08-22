import pytest

from amocrm.services.orders.order_duplicate_checker import AmoCRMOrderDuplicateChecker
from amocrm.services.orders.order_duplicate_checker import AmoCRMOrderDuplicateCheckerException

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def paid_order(user, course, factory):
    return factory.order(user=user, course=course, is_paid=True)


@pytest.fixture
def not_paid_order(factory, user, course):
    return factory.order(user=user, course=course, is_paid=False)


@pytest.fixture
def unfinished_lead(factory, user, course):
    order = factory.order(user=user, course=course, is_paid=False)
    return factory.amocrm_order_lead(order=order)


@pytest.fixture
def duplicate_checker():
    return lambda order: AmoCRMOrderDuplicateChecker(order=order)()


def test_none_if_there_is_paid_order(duplicate_checker, not_paid_order, paid_order):
    got = duplicate_checker(order=not_paid_order)

    assert got is None


def test_new_order_if_has_returned_order(duplicate_checker, not_paid_order, paid_order):
    paid_order.set_not_paid()

    got = duplicate_checker(order=not_paid_order)

    assert got == not_paid_order
    assert not hasattr(got, "amocrm_lead")


def test_new_order_if_no_same_orders(duplicate_checker, not_paid_order):
    got = duplicate_checker(order=not_paid_order)

    assert got == not_paid_order
    assert not hasattr(got, "amocrm_lead")


def test_new_paid_order_if_no_same_orders(duplicate_checker, paid_order):
    got = duplicate_checker(order=paid_order)

    assert got == paid_order
    assert not hasattr(got, "amocrm_lead")


def test_new_order_linked_to_old_unfinished_lead(duplicate_checker, not_paid_order, unfinished_lead):
    got = duplicate_checker(order=not_paid_order)

    assert got == not_paid_order
    assert got.amocrm_lead == unfinished_lead


def test_fails_if_many_lead_for_same_course_and_user(duplicate_checker, factory, not_paid_order):
    orders = factory.cycle(2).order(user=not_paid_order.user, course=not_paid_order.course, is_paid=False)
    for order in orders:
        factory.amocrm_order_lead(order=order)

    with pytest.raises(AmoCRMOrderDuplicateCheckerException, match="There are duplicates for such order with same course and user"):
        duplicate_checker(not_paid_order)


def test_fails_if_order_without_course(duplicate_checker, not_paid_order):
    not_paid_order.course = None
    not_paid_order.save()

    with pytest.raises(AmoCRMOrderDuplicateCheckerException, match="Order has no course"):
        duplicate_checker(not_paid_order)
