from contextlib import nullcontext as does_not_raise
import pytest

from django.contrib.admin.models import CHANGE
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from core import current_user

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("_set_current_user"),
]


@pytest.mark.freeze_time
def test_success_admin_log_created(order):
    order.set_paid()

    log = LogEntry.objects.get()
    assert log.action_flag == CHANGE
    assert log.action_time == timezone.now()
    assert log.change_message == "Order paid"
    assert log.content_type_id == ContentType.objects.get_for_model(order).id
    assert log.object_id == str(order.id)
    assert log.object_repr == str(order)
    assert log.user == current_user.get_current_user()


def test_success_admin_log_created_via_task(order, write_admin_log):
    order.set_paid()

    write_admin_log.assert_called_once()


def test_break_if_current_user_could_not_be_captured(order):
    current_user.unset_current_user()

    with does_not_raise():
        order.set_paid()

    assert LogEntry.objects.get().user == order.user
