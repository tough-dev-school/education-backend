import pytest

from apps.amocrm.models import AmoCRMOrderTransaction
from apps.amocrm.services.orders.order_returner import AmoCRMOrderReturner

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.usefixtures("_set_current_user"),
]


@pytest.fixture
def mock_update_lead(mocker):
    return mocker.patch("apps.amocrm.dto.lead.AmoCRMLeadDTO.update")


@pytest.fixture
def mock_delete_transaction(mocker):
    return mocker.patch("apps.amocrm.dto.transaction.AmoCRMTransactionDTO.delete")


@pytest.fixture
def unpaid_order(mixer, paid_order_with_lead):
    mixer.blend("amocrm.AmoCRMOrderTransaction", order=paid_order_with_lead, amocrm_id=876)
    paid_order_with_lead.refund(paid_order_with_lead.price)
    return paid_order_with_lead


@pytest.fixture
def unpaid_order_not_in_amo(paid_order_without_lead):
    paid_order_without_lead.refund(paid_order_without_lead.price)
    return paid_order_without_lead


@pytest.fixture
def order_returner():
    return lambda order: AmoCRMOrderReturner(order=order)()


def test_correct_calls(order_returner, unpaid_order, mock_update_lead, mock_delete_transaction):
    order_returner(unpaid_order)

    mock_update_lead.assert_called_once_with(status="closed")
    mock_delete_transaction.assert_called_once()


@pytest.mark.usefixtures("mock_delete_transaction", "mock_update_lead")
def test_delete_transaction(order_returner, unpaid_order):
    order_returner(unpaid_order)

    assert AmoCRMOrderTransaction.objects.count() == 0


def test_dont_return_if_not_in_amo(order_returner, unpaid_order_not_in_amo, mock_update_lead, mock_delete_transaction):
    order_returner(unpaid_order_not_in_amo)

    mock_update_lead.assert_not_called()
    mock_delete_transaction.assert_not_called()
