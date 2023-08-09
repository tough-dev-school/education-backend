import pytest

from amocrm.services.orders.order_lead_to_course_linker import AmoCRMOrderLeadToCourseLinker
from amocrm.services.orders.order_lead_to_course_linker import AmoCRMOrderLeadToCourseLinkerException
from amocrm.types import AmoCRMEntityLink
from amocrm.types import AmoCRMEntityLinkMetadata

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def mock_link_entity_to_another_entity(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.link_entity_to_another_entity", return_value=None)


@pytest.fixture(autouse=True)
def _mock_fields_id(mocker):
    mocker.patch("amocrm.services.orders.order_lead_to_course_linker.get_catalog_id", return_value=333)


@pytest.fixture
def lead_course_linker():
    return lambda amocrm_lead: AmoCRMOrderLeadToCourseLinker(amocrm_lead)()


def test_creates_correct_call(lead_course_linker, amocrm_lead, mock_link_entity_to_another_entity):
    lead_course_linker(amocrm_lead)

    mock_link_entity_to_another_entity.assert_called_once_with(
        entity_type="leads",
        entity_id=amocrm_lead.amocrm_id,
        entity_to_link=AmoCRMEntityLink(
            to_entity_id=amocrm_lead.order.course.amocrm_course.amocrm_id,
            to_entity_type="catalog_elements",
            metadata=AmoCRMEntityLinkMetadata(
                quantity=1,
                catalog_id=333,
            ),
        ),
    )


def test_fails_if_no_course(lead_course_linker, amocrm_lead):
    amocrm_lead.order.course.amocrm_course.delete()
    amocrm_lead.order.course.refresh_from_db()

    with pytest.raises(AmoCRMOrderLeadToCourseLinkerException):
        lead_course_linker(amocrm_lead)


@pytest.mark.usefixtures("amocrm_course")
def test_fails_if_transaction_exist(lead_course_linker, amocrm_lead, factory):
    factory.amocrm_order_transaction(order=amocrm_lead.order)

    with pytest.raises(AmoCRMOrderLeadToCourseLinkerException):
        lead_course_linker(amocrm_lead)
