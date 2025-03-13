import pytest
from django.contrib.admin.models import CHANGE, LogEntry
from django.contrib.contenttypes.models import ContentType

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.freeze_time("2032-12-24 15:38"),
]


@pytest.fixture
def create_orders(mocker):
    return mocker.patch("apps.b2b.services.deal_completer.DealCompleter.create_orders")


@pytest.fixture
def assign_existing_orders(mocker):
    return mocker.patch("apps.b2b.services.deal_completer.DealCompleter.assign_existing_orders")


def test_deal_gets_completed(completer, deal):
    completer(deal=deal)()

    deal.refresh_from_db()
    assert deal.completed.year == 2032
    assert deal.completed.month == 12


def test_deal_gets_complete_only_once(completer, create_orders, assign_existing_orders):
    completer()()
    completer()()

    assert create_orders.call_count == 1
    assert assign_existing_orders.call_count == 1


@pytest.mark.auditlog
@pytest.mark.usefixtures("_set_current_user")
def test_auditlog(completer, deal, user):
    completer(deal=deal)()

    log = LogEntry.objects.filter(
        content_type=ContentType.objects.get_for_model(deal).id,
    ).last()
    assert log.action_flag == CHANGE
    assert log.change_message == "Deal completed"
    assert log.user == user
    assert log.object_id == str(deal.id)
    assert log.object_repr == str(deal)
