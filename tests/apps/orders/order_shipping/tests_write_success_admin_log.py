from contextlib import nullcontext as does_not_raise
import pytest

from django.contrib.admin.models import CHANGE
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

pytestmark = pytest.mark.django_db


@pytest.mark.freeze_time
def test_success_admin_log_created(order, user):
    order.set_paid()

    log = LogEntry.objects.get()
    assert log.action_flag == CHANGE
    assert log.action_time == timezone.now()
    assert log.change_message == "Order paid"
    assert log.content_type_id == ContentType.objects.get_for_model(order).id
    assert log.object_id == str(order.id)
    assert log.object_repr == str(order)
    assert log.user == user


def test_success_admin_log_created_via_task(order, write_admin_log):
    order.set_paid()

    write_admin_log.assert_called_once()


def test_do_not_break_if_current_user_could_not_be_captured(another_user, mocker, order):
    mocker.patch("apps.orders.services.order_paid_setter.get_current_user", return_value=None)
    order.update(user=another_user)

    with does_not_raise():
        order.set_paid()

    assert LogEntry.objects.get().user == order.user
