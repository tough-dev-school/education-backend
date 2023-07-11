from collections import Counter
import pytest

from users.tags import StartedTag

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def tag_mechanism():
    return lambda student: StartedTag(student)


@pytest.fixture
def another_unpaid_order(factory, user, another_course_same_group):
    return factory.order(user=user, course=another_course_same_group, paid=None)


@pytest.mark.parametrize("unpaid_orders_quantity", [1, 5])
def test_should_be_applied_if_has_unpaid_order(tag_mechanism, factory, user, unpaid_orders_quantity):
    factory.cycle(unpaid_orders_quantity).order(user=user, paid=None)

    got = tag_mechanism(user).should_be_applied(user)

    assert got is True


@pytest.mark.usefixtures("paid_order")
def test_should_not_be_applied_if_has_no_unpaid_order(tag_mechanism, user):
    got = tag_mechanism(user).should_be_applied(user)

    assert got is False


@pytest.mark.usefixtures("unpaid_order", "another_unpaid_order")
def test_return_list_tags_for_unpaid_courses_and_groups(tag_mechanism, user, course, another_course_same_group):
    course_tag = StartedTag.get_tag_from_slug(course.slug)
    another_course_tag = StartedTag.get_tag_from_slug(another_course_same_group.slug)
    product_group_tag = StartedTag.get_tag_from_slug(course.group.slug)

    got = tag_mechanism(user)()

    got_counter = Counter(got)
    assert got_counter[course_tag] == 1
    assert got_counter[another_course_tag] == 1
    assert got_counter[product_group_tag] == 2  # courses belongs to same group, unique values are responsibility of apply_tags function


@pytest.mark.parametrize("unpaid_orders_quantity", [1, 5, 10])
def test_nplusone_for_unpaid_courses_and_groups(tag_mechanism, user, django_assert_num_queries, unpaid_orders_quantity, factory):
    factory.cycle(unpaid_orders_quantity).order(user=user, paid=None)

    with django_assert_num_queries(2):
        got = tag_mechanism(user)()

    assert len(got) == 2 * unpaid_orders_quantity
