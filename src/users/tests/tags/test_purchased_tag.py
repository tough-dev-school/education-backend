from collections import Counter
import pytest

from django.utils import timezone

from users.tags import PurchasedTag

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def tag_mechanism():
    return lambda student: PurchasedTag(student)


@pytest.fixture
def another_paid_order(factory, user, another_course_same_group):
    return factory.order(user=user, course=another_course_same_group, paid=timezone.now())


@pytest.mark.parametrize("orders_quantity", [1, 5])
def test_should_be_applied_if_has_paid_order(tag_mechanism, factory, user, orders_quantity):
    factory.cycle(orders_quantity).order(user=user, paid=timezone.now())

    got = tag_mechanism(user).should_be_applied(user)

    assert got is True


@pytest.mark.usefixtures("unpaid_order")
def test_should_not_be_applied_if_has_no_unpaid_order(tag_mechanism, user):
    got = tag_mechanism(user).should_be_applied(user)

    assert got is False


@pytest.mark.usefixtures("paid_order", "another_paid_order")
def test_return_list_tags_for_unpaid_courses_and_groups(tag_mechanism, user, course, another_course_same_group):
    course_tag = PurchasedTag.get_tag_from_slug(course.slug)
    another_course_tag = PurchasedTag.get_tag_from_slug(another_course_same_group.slug)
    product_group_tag = PurchasedTag.get_tag_from_slug(course.group.slug)

    got = tag_mechanism(user)()

    got_counter = Counter(got)
    assert got_counter[course_tag] == 1
    assert got_counter[another_course_tag] == 1
    assert got_counter[product_group_tag] == 2  # courses belongs to same group, unique values are responsibility of apply_tags function
