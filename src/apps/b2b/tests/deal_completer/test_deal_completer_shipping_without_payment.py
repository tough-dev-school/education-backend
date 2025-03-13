import pytest
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType

from apps.orders.models import Order

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-24 15:38"),
]


@pytest.fixture
def deal(factory):
    return factory.deal(student_count=1)


def test_deals_get_shipped(completer, deal):
    completer(deal=deal, ship_only=True)()

    deal.refresh_from_db()
    assert deal.shipped_without_payment.year == 2032
    assert deal.shipped_without_payment.month == 12


def test_orders_are_shipped_and_not_paid(completer, deal):
    completer(deal=deal, ship_only=True)()

    order = Order.objects.get(deal=deal)

    assert order.paid is None
    assert order.shipped.year == 2032
    assert order.shipped.month == 12


def test_shipped_and_not_paid_orders_are_getting_paid_when_completer_is_called_for_the_second_time(completer, deal):
    completer(deal=deal, ship_only=True)()
    order = Order.objects.get(deal=deal)

    completer(deal=deal)()
    order.refresh_from_db()

    assert Order.objects.count() == 1, "No new orders created"
    assert order.paid is not None
    assert order.shipped is not None


@pytest.mark.auditlog
@pytest.mark.usefixtures("_set_current_user")
def test_auditlog_for_shipment(completer, deal, user):
    completer(deal=deal, ship_only=True)()

    log = LogEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(deal).id,
    ).last()
    assert log.action_flag == CHANGE
    assert log.change_message == "Deal shipped without payment"
    assert log.user == user
    assert log.object_id == str(deal.id)
    assert log.object_repr == str(deal)


@pytest.mark.auditlog
@pytest.mark.usefixtures("_set_current_user")
def test_auditlog_for_shipment_and_payments(completer, deal):
    completer(deal=deal, ship_only=True)()
    completer(deal=deal)()

    logs = list(
        LogEntry.objects.filter(
            content_type=ContentType.objects.get_for_model(deal).id,
        )
        .order_by("-action_time")
        .all()
    )

    assert len(logs) == 2, "Two log entries created, first for shipment and second for payment"
    assert logs[0].change_message == "Deal shipped without payment"
    assert logs[1].change_message == "Deal completed"
