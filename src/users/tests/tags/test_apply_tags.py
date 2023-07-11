import pytest

from django.utils import timezone

from users.tags.pipeline import apply_tags

pytestmark = [pytest.mark.django_db]


@pytest.mark.usefixtures("paid_order", "unpaid_order")
def test_tags_append_once(user):
    apply_tags(user)
    apply_tags(user)

    assert len(user.tags) > 0
    assert len(user.tags) == len(set(user.tags))


@pytest.mark.parametrize("quantity", [1, 3, 7])
def test_nplusone(user, factory, course, another_course_same_group, quantity, django_assert_num_queries):
    for _ in range(quantity):
        factory.order(user=user, course=course, paid=None)
        factory.order(user=user, course=course, paid=timezone.now(), price=4815)
        factory.order(user=user, course=another_course_same_group, paid=None)

    with django_assert_num_queries(4):
        apply_tags(user)
