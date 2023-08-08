import pytest

from amocrm.services.contact_updater import AmoCRMContactUpdater
from amocrm.types import AmoCRMCatalogElement

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def amocrm_user_contact(factory, user):
    return factory.amocrm_user_contact(user=user, amocrm_id=999)


@pytest.fixture
def updated_contact(contact_fields):
    return AmoCRMCatalogElement(id=999, name="Vlad Drac", custom_fields_values=contact_fields)


@pytest.fixture
def mock_update_contact(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.update_contact", return_value=999)


@pytest.fixture
def contact_updater():
    return lambda amocrm_user_contact: AmoCRMContactUpdater(amocrm_user_contact)()


def test_updates_correct_call(contact_updater, amocrm_user_contact, mock_update_contact, updated_contact):
    contact_updater(amocrm_user_contact)

    mock_update_contact.assert_called_once_with(
        user_as_contact_element=updated_contact,
    )


@pytest.mark.usefixtures("mock_update_contact")
def test_update_amocrm_course(contact_updater, amocrm_user_contact):
    got = contact_updater(amocrm_user_contact)

    assert got == amocrm_user_contact.amocrm_id
