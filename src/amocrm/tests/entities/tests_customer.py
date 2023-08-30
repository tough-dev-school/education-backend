import pytest

from amocrm.entities import AmoCRMCustomer

pytestmark = [
    pytest.mark.django_db,
]


@pytest.fixture
def successful_response():
    return {
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
def _successful_create_response(post, successful_response):
    post.return_value = successful_response


@pytest.fixture
def _successful_update_response(patch, successful_response):
    patch.return_value = successful_response


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


@pytest.mark.usefixtures("_successful_create_response")
def test_create_customer(user, post):
    got = AmoCRMCustomer(user=user).create()

    assert got == 1369385
    post.assert_called_once_with(
        url="/api/v4/customers",
        data=[
            {
                "name": "First Last",
                "_embedded": {"tags": [{"name": "b2b"}, {"name": "any-purchase"}]},
            },
        ],
    )


@pytest.mark.usefixtures("_successful_update_response")
def test_update_customer(user, patch):
    AmoCRMCustomer(user=user).update(customer_id=5555)

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


@pytest.mark.usefixtures("_successful_link_response")
def test_link_to_contact(user, post):
    AmoCRMCustomer(user=user).link_to_contact(customer_id=5555, contact_id=8888)

    post.assert_called_once_with(
        url="/api/v4/customers/5555/link",
        data=[
            {
                "to_entity_id": 8888,
                "to_entity_type": "contacts",
            },
        ],
    )
