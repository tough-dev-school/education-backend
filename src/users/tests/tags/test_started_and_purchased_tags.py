import pytest

from django.utils import timezone

from users.tags.pipeline import apply_tags

pytestmark = [pytest.mark.django_db]


@pytest.mark.usefixtures("unpaid_order")
def test_order_started(user):
    apply_tags(user)

    assert "popug-3-self__started" in user.tags
    assert "popug-3__started" in user.tags


@pytest.mark.usefixtures("paid_order")
def test_order_purchased(user):
    apply_tags(user)

    assert "popug-3-self__purchased" in user.tags
    assert "popug-3__purchased" in user.tags


def test_order_started_and_then_purchased(user, unpaid_order):
    unpaid_order.paid = timezone.now()
    unpaid_order.save()

    apply_tags(user)

    assert "popug-3-self__started" not in user.tags
    assert "popug-3__started" not in user.tags
    assert "popug-3-self__purchased" in user.tags
    assert "popug-3__purchased" in user.tags


@pytest.mark.usefixtures("unpaid_order", "paid_order")
def test_one_unpaid_and_one_paid_order_for_same_course(user):
    apply_tags(user)

    assert "popug-3-self__started" not in user.tags
    assert "popug-3__started" not in user.tags
    assert "popug-3-self__purchased" in user.tags
    assert "popug-3__purchased" in user.tags


@pytest.mark.usefixtures("paid_order")
def test_one_unpaid_and_one_paid_order_for_same_product_group(user, unpaid_order, another_course_same_group):
    unpaid_order.course = another_course_same_group
    unpaid_order.save()

    apply_tags(user)

    assert "popug-3-self__started" not in user.tags
    assert "popug-3__started" not in user.tags
    assert "popug-3-self__purchased" in user.tags
    assert "popug-3__purchased" in user.tags
