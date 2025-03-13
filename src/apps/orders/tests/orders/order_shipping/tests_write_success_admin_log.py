import pytest
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

pytestmark = [
    pytest.mark.auditlog,
    pytest.mark.django_db,
]


@pytest.fixture
def order(factory):
    return factory.order()


@pytest.mark.freeze_time
@pytest.mark.usefixtures("_set_current_user")
def test_paid_log_created(order, user):
    order.set_paid()

    logs = list(LogEntry.objects.order_by("-id").all())

    # first one is for payment
    assert logs[0].action_flag == CHANGE
    assert logs[0].action_time == timezone.now()
    assert logs[0].change_message == "Order paid"
    assert logs[0].content_type_id == ContentType.objects.get_for_model(order).id
    assert logs[0].object_id == str(order.id)
    assert logs[0].object_repr == str(order)
    assert logs[0].user == user

    # second one is for shipment
    assert logs[1].action_flag == CHANGE
    assert logs[1].action_time == timezone.now()
    assert logs[1].change_message == "Order shipped"
    assert logs[1].content_type_id == ContentType.objects.get_for_model(order).id
    assert logs[1].object_id == str(order.id)
    assert logs[1].object_repr == str(order)
    assert logs[1].user == user


@pytest.mark.freeze_time
@pytest.mark.usefixtures("_set_current_user")
def test_shipping_without_payment(order, user):
    order.ship_without_payment()
    log = LogEntry.objects.last()
    assert log.action_flag == CHANGE
    assert log.action_time == timezone.now()
    assert log.change_message == "Order shipped"
    assert log.content_type_id == ContentType.objects.get_for_model(order).id
    assert log.object_id == str(order.id)
    assert log.object_repr == str(order)
    assert log.user == user


def test_log_author_is_student_when_set_paid_by_anon(order):
    order.set_paid()

    logs = list(LogEntry.objects.order_by("-id").all())

    assert logs[0].user == order.user
    assert logs[1].user == order.user
