import pytest

from amocrm.models import AmoCRMOrderLead
from amocrm.services.orders.lead_creator import AmoCRMLeadCreator
from amocrm.services.orders.lead_creator import AmoCRMLeadCreatorException

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _mock_fields_id(mocker):
    mocker.patch("amocrm.services.orders.lead_creator.get_b2c_pipeline_id", return_value=777)
    mocker.patch("amocrm.services.orders.lead_creator.get_b2c_pipeline_status_id", return_value=999)
    mocker.patch("amocrm.services.orders.lead_creator.get_catalog_id", return_value=555)


@pytest.fixture(autouse=True)
def mock_create_lead(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.create_lead", return_value=481516)


@pytest.fixture(autouse=True)
def mock_update_lead(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.update_lead", return_value=481516)


@pytest.fixture(autouse=True)
def mock_link_entity_to_another_entity(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.link_entity_to_another_entity", return_value=None)


@pytest.fixture
def lead_creator():
    return lambda order: AmoCRMLeadCreator(order=order)()


def test_creates_amocrm_order_lead(lead_creator, order):
    lead_creator(order)

    amocrm_lead = AmoCRMOrderLead.objects.get()
    assert amocrm_lead.order == order
    assert amocrm_lead.amocrm_id == 481516


def test_creates_correct_call(lead_creator, order, mock_create_lead, mock_update_lead, mock_link_entity_to_another_entity):
    lead_creator(order)

    mock_create_lead.assert_called_once()
    mock_link_entity_to_another_entity.assert_called_once()
    mock_update_lead.assert_called_once()


def test_fails_if_already_exist(lead_creator, order, factory):
    factory.amocrm_order_lead(order=order)

    with pytest.raises(AmoCRMLeadCreatorException, match="Lead already exist"):
        lead_creator(order)


def test_fails_if_transaction_already_exist(lead_creator, order, factory):
    factory.amocrm_order_transaction(order=order)

    with pytest.raises(AmoCRMLeadCreatorException, match="Transaction for this order already exists"):
        lead_creator(order)


def test_fails_if_no_amocrm_course(lead_creator, order):
    order.course.amocrm_course.delete()
    order.refresh_from_db()

    with pytest.raises(AmoCRMLeadCreatorException, match="Course doesn't exist in AmoCRM"):
        lead_creator(order)


def test_fails_if_no_amocrm_contact(lead_creator, order):
    order.user.amocrm_user.delete()
    order.refresh_from_db()

    with pytest.raises(AmoCRMLeadCreatorException, match="AmoCRM contact for order's user doesn't exist"):
        lead_creator(order)
