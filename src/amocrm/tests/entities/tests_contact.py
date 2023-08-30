import pytest

from amocrm.entities import AmoCRMContact

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture(autouse=True)
def mock_contact_field_id(mocker):
    return mocker.patch("amocrm.entities.contact.get_contact_field_id", return_value=2235143)


@pytest.fixture
def _successful_create_response(post):
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
def _successful_update_response(patch):
    patch.return_value = {
        "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/contacts"}},
        "_embedded": {
            "contacts": [
                {
                    "id": 72845935,
                    "name": "First Last",
                    "updated_at": 1691474691,
                    "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/contacts/72845935"}},
                }
            ]
        },
    }


@pytest.mark.usefixtures("_successful_create_response")
def test_create_contact(user, post):
    got = AmoCRMContact(user=user).create()

    assert got == 72845935
    post.assert_called_once_with(
        url="/api/v4/contacts",
        data=[
            {
                "name": "First Last",
                "custom_fields_values": [
                    {"field_id": 2235143, "values": [{"value": "dada@da.net"}]},
                ],
            },
        ],
    )


@pytest.mark.usefixtures("_successful_update_response")
def test_update_contact(user, patch):
    AmoCRMContact(user=user).update(contact_id=5555)

    patch.assert_called_once_with(
        url="/api/v4/contacts",
        data=[
            {
                "id": 5555,
                "name": "First Last",
                "custom_fields_values": [
                    {"field_id": 2235143, "values": [{"value": "dada@da.net"}]},
                ],
            },
        ],
    )
