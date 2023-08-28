import pytest

from amocrm.services.orders.order_deleter import AmoCRMOrderDeleter
from amocrm.services.orders.order_deleter import AmoCRMOrderDeleterException

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _mock_b2c_fields_id(mocker):
    mocker.patch("amocrm.services.orders.order_deleter.get_pipeline_id", return_value=777)
    mocker.patch("amocrm.services.orders.order_deleter.get_b2c_pipeline_status_id", return_value=999)


@pytest.fixture
def mock_update_lead(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.update_lead", return_value=481516)


@pytest.fixture
def mock_delete_transaction(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.delete_transaction", return_value=None)


@pytest.fixture
def unpaid_order(factory, paid_order_with_lead):
    factory.amocrm_order_transaction(order=paid_order_with_lead, amocrm_id=876)
    paid_order_with_lead.set_not_paid()
    return paid_order_with_lead


@pytest.fixture
def order_deleter():
    return lambda order: AmoCRMOrderDeleter(order=order)()


def test_correct_calls(order_deleter, unpaid_order, mock_update_lead, mock_delete_transaction):
    order_deleter(unpaid_order)

    mock_update_lead.assert_called_once_with(
        lead_id=unpaid_order.amocrm_lead.amocrm_id,
        status_id=999,
        pipeline_id=777,
        price=unpaid_order.price,
        created_at=unpaid_order.created,
    )
    mock_delete_transaction.assert_called_once_with(transaction_id=unpaid_order.amocrm_transaction.amocrm_id)


def test_fails_if_transaction_doesnt_exist(order_deleter, unpaid_order, factory):
    unpaid_order.amocrm_transaction.delete()
    unpaid_order.refresh_from_db()

    with pytest.raises(AmoCRMOrderDeleterException, match="Transaction for this unpaid order doesn't exists"):
        order_deleter(unpaid_order)
