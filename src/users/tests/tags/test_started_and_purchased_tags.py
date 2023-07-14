import pytest

from users.tags.pipeline import generate_tags

pytestmark = [pytest.mark.django_db]


@pytest.mark.usefixtures("non_paid_order")
def test_order_started(user):
    generate_tags(user)

    assert "popug-3-self__started" in user.tags
    assert "popug-3__started" in user.tags


@pytest.mark.usefixtures("paid_order")
def test_order_purchased(user):
    generate_tags(user)

    assert "popug-3-self__purchased" in user.tags
    assert "popug-3__purchased" in user.tags


def test_order_started_and_then_purchased(user, non_paid_order):
    non_paid_order.set_paid()

    generate_tags(user)

    assert "popug-3-self__started" not in user.tags
    assert "popug-3__started" not in user.tags
    assert "popug-3-self__purchased" in user.tags
    assert "popug-3__purchased" in user.tags


def test_started_and_purchased_orders_for_same_course(user, factory):
    course_no_group = factory.course(slug="how-to-be-007", group=None, price=14)
    factory.order(is_paid=False, item=course_no_group, user=user)
    factory.order(is_paid=True, item=course_no_group, user=user)

    generate_tags(user)

    assert "how-to-be-007__purchased" in user.tags
    assert "how-to-be-007__started" not in user.tags
    assert "how-to-be__purchased" not in user.tags  # there is no group, no tag for no group
    assert "how-to-be__started" not in user.tags


def test_started_and_purchased_orders_for_same_product_group(user, course, factory):
    another_course_same_group = factory.course(slug=f"{course.group.slug}-vip", group=course.group)
    factory.order(is_paid=False, item=another_course_same_group, user=user)
    factory.order(is_paid=True, item=course, user=user)

    generate_tags(user)

    assert "popug-3-vip__started" not in user.tags
    assert "popug-3-self__started" not in user.tags
    assert "popug-3__started" not in user.tags  # user purchased at least one course from this group
    assert "popug-3-vip__purchased" not in user.tags
    assert "popug-3-self__purchased" in user.tags
    assert "popug-3__purchased" in user.tags
