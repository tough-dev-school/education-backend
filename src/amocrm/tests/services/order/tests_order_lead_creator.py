import pytest

from amocrm.models import AmoCRMOrderLead
from amocrm.services.orders.order_lead_creator import AmoCRMOrderLeadCreator
from amocrm.services.orders.order_lead_creator import AmoCRMOrderLeadCreatorException
from amocrm.types import AmoCRMEntityLink
from amocrm.types import AmoCRMEntityLinkMetadata

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def _mock_fields_id(mocker):
    mocker.patch("amocrm.services.orders.order_lead_creator.get_pipeline_id", return_value=777)
    mocker.patch("amocrm.services.orders.order_lead_creator.get_b2c_pipeline_status_id", return_value=999)
    mocker.patch("amocrm.services.orders.order_lead_creator.get_catalog_id", return_value=555)


@pytest.fixture(autouse=True)
def mock_create_lead(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.create_lead", return_value=481516)


@pytest.fixture(autouse=True)
def mock_link_entity_to_another_entity(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.link_entity_to_another_entity", return_value=None)


@pytest.fixture
def lead_creator():
    return lambda order: AmoCRMOrderLeadCreator(order=order)()


def test_creates_amocrm_order_lead(lead_creator, order):
    got = lead_creator(order)

    amocrm_lead = AmoCRMOrderLead.objects.get()
    assert got == amocrm_lead.amocrm_id
    assert amocrm_lead.order == order
    assert amocrm_lead.amocrm_id == 481516


def test_creates_correct_call(lead_creator, order, mock_create_lead, mock_link_entity_to_another_entity):
    lead_creator(order)

    mock_create_lead.assert_called_once_with(
        status_id=999,
        pipeline_id=777,
        contact_id=order.user.amocrm_user_contact.amocrm_id,
        price=order.price,
        created_at=order.created,
    )
    mock_link_entity_to_another_entity.assert_called_once_with(
        entity_type="leads",
        entity_id=481516,
        entity_to_link=AmoCRMEntityLink(
            to_entity_id=order.course.amocrm_course.amocrm_id,
            to_entity_type="catalog_elements",
            metadata=AmoCRMEntityLinkMetadata(
                quantity=1,
                catalog_id=555,
            ),
        ),
    )


def test_fails_if_already_exist(lead_creator, order, factory):
    factory.amocrm_order_lead(order=order)

    with pytest.raises(AmoCRMOrderLeadCreatorException, match="Lead already exist"):
        lead_creator(order)


def test_fails_if_transaction_already_exist(lead_creator, order, factory):
    factory.amocrm_order_transaction(order=order)

    with pytest.raises(AmoCRMOrderLeadCreatorException, match="Transaction for this order already exists"):
        lead_creator(order)


def test_fails_if_no_amocrm_course(lead_creator, order):
    order.course.amocrm_course.delete()
    order.refresh_from_db()

    with pytest.raises(AmoCRMOrderLeadCreatorException, match="Course doesn't exist in AmoCRM"):
        lead_creator(order)


def test_fails_if_no_amocrm_contact(lead_creator, order):
    order.user.amocrm_user_contact.delete()
    order.refresh_from_db()

    with pytest.raises(AmoCRMOrderLeadCreatorException, match="AmoCRM contact for order's user doesn't exist"):
        lead_creator(order)
