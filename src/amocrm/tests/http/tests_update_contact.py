import pytest

from amocrm.types import AmoCRMCatalogElement
from amocrm.types import AmoCRMCatalogElementField
from amocrm.types import AmoCRMCatalogElementFieldValue

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def _successful_response(patch):
    patch.return_value = {
        "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/contacts"}},
        "_embedded": {
            "contacts": [
                {
                    "id": 72845935,
                    "name": "Test CoCoCo",
                    "updated_at": 1691474691,
                    "is_deleted": False,
                    "is_unsorted": False,
                    "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/contacts/72845935"}},
                }
            ]
        },
    }


@pytest.fixture
def contact_fields():
    email_field_value = AmoCRMCatalogElementFieldValue(value="coco@co.meow")
    return [
        AmoCRMCatalogElementField(field_id=2235143, values=[email_field_value]),
    ]


@pytest.fixture
def contact(contact_fields):
    return AmoCRMCatalogElement(id=72845935, name="Test CoCoCo", custom_fields_values=contact_fields)


@pytest.mark.usefixtures("_successful_response")
def test_update_contact(amocrm_client, contact):
    got = amocrm_client.update_contact(user_as_contact_element=contact)

    assert got == 72845935


@pytest.mark.usefixtures("_successful_response")
def test_update_contact_patch_correct_params(user, amocrm_client, patch, contact):
    amocrm_client.update_contact(user_as_contact_element=contact)

    patch.assert_called_once_with(
        url="/api/v4/contacts",
        data=[
            {
                "id": 72845935,
                "name": "Test CoCoCo",
                "custom_fields_values": [
                    {"field_id": 2235143, "values": [{"value": "coco@co.meow"}]},
                ],
            },
        ],
    )
