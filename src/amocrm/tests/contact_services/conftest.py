import pytest

from amocrm.types import AmoCRMCatalogElementField
from amocrm.types import AmoCRMCatalogElementFieldValue


@pytest.fixture
def contact_fields():
    email_value = AmoCRMCatalogElementFieldValue(value="vald@drac.ro")
    return [
        AmoCRMCatalogElementField(field_id=333, values=[email_value]),
    ]


@pytest.fixture
def user(user):
    user.first_name = "Vlad"
    user.last_name = "Drac"
    user.email = "vald@drac.ro"
    user.save()
    return user


@pytest.fixture(autouse=True)
def _mock_fields_id(mocker):
    mocker.patch("amocrm.services.contact_creator.get_contact_field_id", return_value=333)
    mocker.patch("amocrm.services.contact_updater.get_contact_field_id", return_value=333)
