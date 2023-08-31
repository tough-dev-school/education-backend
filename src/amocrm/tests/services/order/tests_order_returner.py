import pytest

from amocrm.services.orders.order_returner import AmoCRMOrderReturner

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def mock_update_lead(mocker):
    return mocker.patch("amocrm.dto.lead.AmoCRMLead.update")


@pytest.fixture
def mock_delete_transaction(mocker):
    return mocker.patch("amocrm.dto.transaction.AmoCRMTransaction.delete")


@pytest.fixture
def unpaid_order(factory, paid_order_with_lead):
    factory.amocrm_order_transaction(order=paid_order_with_lead, amocrm_id=876)
    paid_order_with_lead.set_not_paid()
    return paid_order_with_lead


@pytest.fixture
def order_deleter():
    return lambda order: AmoCRMOrderReturner(order=order)()


def test_correct_calls(order_deleter, unpaid_order, mock_update_lead, mock_delete_transaction):
    order_deleter(unpaid_order)

    mock_update_lead.assert_called_once_with(status="closed")
    mock_delete_transaction.assert_called_once()
