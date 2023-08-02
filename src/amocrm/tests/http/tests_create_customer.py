import pytest

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def _successful_response(post):
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


@pytest.mark.usefixtures("_successful_response")
def test_create_customer_request_fields(user, amocrm_client, post):
    user.first_name = "First"
    user.last_name = "Last"
    user.tags = ["b2b", "any-purchase"]
    user.save()

    got = amocrm_client.create_customer(user)

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


@pytest.mark.usefixtures("_successful_response")
def test_create_anonymous_customer(user, amocrm_client, post):
    user.first_name = ""
    user.last_name = ""
    user.tags = []
    user.save()

    got = amocrm_client.create_customer(user)

    assert got == 1369385
    post.assert_called_once_with(
        url="/api/v4/customers",
        data=[
            {
                "name": "Anonymous",
                "_embedded": {"tags": []},
            },
        ],
    )
