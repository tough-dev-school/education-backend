import pytest

from amocrm.types import AmoCRMElement
from amocrm.types import AmoCRMElementField
from amocrm.types import AmoCRMElementFieldValue

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def _successful_response(post):
    post.return_value = {
        "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/contacts"}},
        "_embedded": {
            "contacts": [
                {
                    "id": 72845935,
                    "is_deleted": False,
                    "is_unsorted": False,
                    "request_id": "0",
                    "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/contacts/72845935"}},
                }
            ]
        },
    }


@pytest.fixture
def contact_fields():
    email_field_value = AmoCRMElementFieldValue(value="dada@da.net")
    return [
        AmoCRMElementField(field_id=2235143, values=[email_field_value]),
    ]


@pytest.fixture
def contact(contact_fields):
    return AmoCRMElement(name="Some Contact", custom_fields_values=contact_fields)


@pytest.mark.usefixtures("_successful_response")
def test_create_contact(amocrm_client, contact):
    got = amocrm_client.create_contact(user_as_contact_element=contact)

    assert got == 72845935


@pytest.mark.usefixtures("_successful_response")
def test_create_contact_post_correct_params(amocrm_client, post, contact):
    amocrm_client.create_contact(user_as_contact_element=contact)

    post.assert_called_once_with(
        url="/api/v4/contacts",
        data=[
            {
                "name": "Some Contact",
                "custom_fields_values": [
                    {"field_id": 2235143, "values": [{"value": "dada@da.net"}]},
                ],
            },
        ],
    )
