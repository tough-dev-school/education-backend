import pytest


pytestmark = [pytest.mark.django_db]


def test_setting_order_as_paid_does_not_generate_too_much_sql(factory, django_assert_max_num_queries):
    with django_assert_max_num_queries(10):
        factory.order(is_paid=True)
