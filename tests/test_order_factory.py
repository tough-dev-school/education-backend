import pytest


pytestmark = [pytest.mark.django_db]


def test(factory, django_assert_max_num_queries):
    with django_assert_max_num_queries(11):
        factory.order(is_paid=True)
