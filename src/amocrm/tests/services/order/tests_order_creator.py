import pytest

from amocrm.services.orders.order_creator import AmoCRMOrderCreator
from amocrm.services.orders.order_creator import AmoCRMOrderCreatorException
from amocrm.types import AmoCRMTransactionElement
from amocrm.types import AmoCRMTransactionElementMetadata

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _mock_b2c_fields_id(mocker):
    mocker.patch("amocrm.services.orders.order_creator.get_pipeline_id", return_value=777)
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

    mock_update_lead.assert_called_once_with(
        lead_id=paid_order_with_lead.amocrm_lead.amocrm_id,
        status_id=999,
        pipeline_id=777,
        price=paid_order_with_lead.price,
        created_at=paid_order_with_lead.created,
    )
    mock_create_transaction.assert_called_once_with(
        customer_id=paid_order_with_lead.user.amocrm_user.amocrm_id,
        price=paid_order_with_lead.price,
        order_slug=paid_order_with_lead.slug,
        purchased_product=AmoCRMTransactionElement(
            id=paid_order_with_lead.course.amocrm_course.amocrm_id,
            metadata=AmoCRMTransactionElementMetadata(
                catalog_id=555,
                quantity=1,
            ),
        ),
    )


def test_fails_if_transaction_already_exist(order_creator, paid_order_with_lead, factory):
    factory.amocrm_order_transaction(order=paid_order_with_lead)

    with pytest.raises(AmoCRMOrderCreatorException, match="Transaction for this paid order already exists"):
        order_creator(paid_order_with_lead)


def test_fails_if_no_customer(order_creator, paid_order_with_lead):
    paid_order_with_lead.user.amocrm_user.delete()
    paid_order_with_lead.refresh_from_db()

    with pytest.raises(AmoCRMOrderCreatorException, match="AmoCRM customer for order's user doesn't exist"):
        order_creator(paid_order_with_lead)
