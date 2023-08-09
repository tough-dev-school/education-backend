import pytest

from amocrm.services.contacts.contact_to_customer_linker import AmoCRMContactToCustomerLinker
from amocrm.services.contacts.contact_to_customer_linker import AmoCRMContactToCustomerLinkerException
from amocrm.types import AmoCRMEntityLink

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def mock_link_entity_to_another_entity(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.link_entity_to_another_entity", return_value=None)


@pytest.fixture
def contact_customer_linker():
    return lambda user: AmoCRMContactToCustomerLinker(user)()


@pytest.fixture
def amocrm_contact(factory, user):
    return factory.amocrm_user_contact(user=user, amocrm_id=888)


@pytest.fixture
def amocrm_customer(factory, user):
    return factory.amocrm_user(user=user, amocrm_id=555)


@pytest.mark.usefixtures("amocrm_contact", "amocrm_customer")
def test_creates_correct_call(contact_customer_linker, user, mock_link_entity_to_another_entity):
    contact_customer_linker(user)

    mock_link_entity_to_another_entity.assert_called_once_with(
        entity_type="customers",
        entity_id=555,
        entity_to_link=AmoCRMEntityLink(
            to_entity_id=888,
            to_entity_type="contacts",
        ),
    )


@pytest.mark.usefixtures("amocrm_customer")
def test_fails_if_no_contact(contact_customer_linker, user):
    with pytest.raises(AmoCRMContactToCustomerLinkerException):
        contact_customer_linker(user)


@pytest.mark.usefixtures("amocrm_contact")
def test_fails_if_no_customer(contact_customer_linker, user):
    with pytest.raises(AmoCRMContactToCustomerLinkerException):
        contact_customer_linker(user)
