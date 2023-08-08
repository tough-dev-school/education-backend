import pytest

from amocrm.models import AmoCRMUserContact
from amocrm.services.contacts.contact_creator import AmoCRMContactCreator
from amocrm.services.contacts.contact_creator import AmoCRMContactCreatorException
from amocrm.types import AmoCRMCatalogElement

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture(autouse=True)
def mock_create_contact(mocker):
    return mocker.patch("amocrm.client.AmoCRMClient.create_contact", return_value=999)


@pytest.fixture
def contact_creator():
    return lambda user: AmoCRMContactCreator(user)()


def test_creates_amocrm_contact(contact_creator, user):
    got = contact_creator(user)

    amocrm_contact = AmoCRMUserContact.objects.get()
    assert got == amocrm_contact.amocrm_id
    assert amocrm_contact.user == user
    assert amocrm_contact.amocrm_id == 999


def test_creates_correct_call(contact_creator, user, mock_create_contact, contact_fields):
    contact_creator(user)

    mock_create_contact.assert_called_once_with(
        user_as_contact_element=AmoCRMCatalogElement(name="Vlad Drac", custom_fields_values=contact_fields),
    )


def test_fails_if_already_exist(contact_creator, user, factory):
    factory.amocrm_user_contact(user=user)

    with pytest.raises(AmoCRMContactCreatorException):
        contact_creator(user)
