import pytest

from amocrm.entities import AmoCRMCustomer

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def _successful_create_customer_response(post):
    post.return_value = {
        "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/customers"}},
        "_embedded": {
            "customers": [
                {
                    "id": 1369385,
                    "name": "Some name",
                    "status_id": 25008378,
                    "created_by": 0,
                    "updated_by": 0,
                    "created_at": 1690793002,
                    "updated_at": 1690793002,
                    "account_id": 31204626,
                    "request_id": "0",
                    "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/customers/1369385"}},
                }
            ]
        },
    }


@pytest.fixture
def _successful_create_contact_response(post):
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
def _successful_link_response(post):
    post.return_value = {
        "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/customers/5555/links"}},
        "_embedded": {
            "links": [
                {"to_entity_id": 8888, "to_entity_type": "contacts", "metadata": None},
            ],
        },
    }


@pytest.mark.usefixtures("_successful_create_contact_response")
def test_create_contact_response(user, post):
    got = AmoCRMCustomer(user=user).create_contact()

    assert got == 72845935


def test_create_contact(user, post):
    AmoCRMCustomer(user=user).create_contact()

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


def test_update_contact(user, patch):
    AmoCRMCustomer(user=user).update_contact(contact_id=5555)

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


@pytest.mark.usefixtures("_successful_create_customer_response")
def test_create_customer_response(user, post):
    got = AmoCRMCustomer(user=user).create_customer()

    assert got == 1369385


def test_create_customer(user, post):
    AmoCRMCustomer(user=user).create_customer()

    post.assert_called_once_with(
        url="/api/v4/customers",
        data=[
            {
                "name": "First Last",
                "_embedded": {"tags": [{"name": "b2b"}, {"name": "any-purchase"}]},
            },
        ],
    )


def test_update_customer(user, patch):
    AmoCRMCustomer(user=user).update_customer(customer_id=5555)

    patch.assert_called_once_with(
        url="/api/v4/customers",
        data=[
            {
                "id": 5555,
                "name": "First Last",
                "_embedded": {"tags": [{"name": "b2b"}, {"name": "any-purchase"}]},
            },
        ],
    )


def test_link_customer_to_contact(user, post):
    AmoCRMCustomer(user=user).link_customer_to_contact(customer_id=5555, contact_id=8888)

    post.assert_called_once_with(
        url="/api/v4/customers/5555/link",
        data=[
            {
                "to_entity_id": 8888,
                "to_entity_type": "contacts",
            },
        ],
    )
