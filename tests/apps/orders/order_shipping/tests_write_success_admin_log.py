from contextlib import nullcontext as does_not_raise
import pytest

from django.contrib.admin.models import CHANGE
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

pytestmark = pytest.mark.django_db


@pytest.mark.freeze_time
def test_success_admin_log_created(mocker, order, user):
    mocker.patch("apps.orders.services.order_shipper.OrderShipper.write_success_admin_log")

    order.set_paid()

    log = LogEntry.objects.last()
    assert log.action_flag == CHANGE
    assert log.action_time == timezone.now()
    assert log.change_message == "Order paid"
    assert log.content_type_id == ContentType.objects.get_for_model(order).id
    assert log.object_id == str(order.id)
    assert log.object_repr == str(order)
    assert log.user == user


def test_do_not_break_if_current_user_could_not_be_captured(mocker, order, user):
    mocker.patch("apps.orders.services.order_paid_setter.get_current_user", return_value=None)
    mocker.patch("apps.orders.services.order_shipper.OrderShipper.write_success_admin_log")

    with does_not_raise():
        order.set_paid()

    assert LogEntry.objects.get().user == order.user
