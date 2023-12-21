from contextlib import nullcontext as does_not_raise
import pytest

from django.contrib.admin.models import CHANGE
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from core import current_user

pytestmark = [
    pytest.mark.auditlog,
    pytest.mark.django_db,
]


@pytest.fixture
def order(factory):
    return factory.order()


@pytest.mark.freeze_time
def test_paid_log_created(order, user):
    order.set_paid()

    log = LogEntry.objects.get()
    assert log.action_flag == CHANGE
    assert log.action_time == timezone.now()
    assert log.change_message == "Order paid"
    assert log.content_type_id == ContentType.objects.get_for_model(order).id
    assert log.object_id == str(order.id)
    assert log.object_repr == str(order)
    assert log.user == user


def test_log_author_is_student_when_set_paid_by_anon(mocker, order):
    mocker.patch("apps.orders.services.order_paid_setter.get_current_user", return_value=None)

    order.set_paid()

    assert LogEntry.objects.get().user == order.user
