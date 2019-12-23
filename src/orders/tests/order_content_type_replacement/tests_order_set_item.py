import pytest

from orders.models import UnknownItemException

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def order(order):
    """Empty order"""
    return order()


def test_record(order, record):
    order.set_item(record)
    order.save()

    order.refresh_from_db()

    assert order.record == record


def test_course(order, course):
    order.set_item(course)
    order.save()

    order.refresh_from_db()

    assert order.course == course


def test_bundle(order, bundle):
    order.set_item(bundle)
    order.save()

    order.refresh_from_db()

    assert order.bundle == bundle


def test_exception_when_there_is_not_foreignkey(order):
    with pytest.raises(UnknownItemException):
        order.set_item(order)


def test_setting_new_item_removes_the_old_one(order, course, bundle):
    order.set_item(course)
    order.save()

    order.set_item(bundle)
    order.save()

    order.refresh_from_db()

    assert order.bundle == bundle
    assert order.course is None
