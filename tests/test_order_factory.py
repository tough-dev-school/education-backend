import pytest

from django.contrib.contenttypes.models import ContentType


pytestmark = [pytest.mark.django_db]


def test_setting_order_as_paid_does_not_generate_too_much_sql(factory, django_assert_num_queries, mocker):
    mocker.patch("apps.orders.services.order_shipper.OrderShipper.write_success_admin_log")

    ContentType.objects.clear_cache()

    with django_assert_num_queries(12):
        factory.order(is_paid=True)

    with django_assert_num_queries(11):
        factory.order(is_paid=True)
