import pytest

from amocrm.services.orders.order_creator import AmoCRMOrderCreator

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _mock_fields_id(mocker):
    mocker.patch("amocrm.services.orders.order_creator.get_b2c_pipeline_id", return_value=777)
    mocker.patch("amocrm.services.orders.order_creator.get_b2c_pipeline_status_id", return_value=999)
    mocker.patch("amocrm.services.orders.order_creator.get_catalog_id", return_value=555)


@pytest.fixture
def mock_update_lead(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.update_lead", return_value=481516)


@pytest.fixture
def mock_create_transaction(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.create_customer_transaction", return_value=2342)


@pytest.fixture
def order_creator():
    return lambda order: AmoCRMOrderCreator(order=order)()


def test_updates_correct_calls(order_creator, paid_order_with_lead, mock_update_lead, mock_create_transaction):
    order_creator(paid_order_with_lead)

    mock_update_lead.assert_called_once()
    mock_create_transaction.assert_called_once()
