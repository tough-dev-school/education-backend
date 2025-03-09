import pytest

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
