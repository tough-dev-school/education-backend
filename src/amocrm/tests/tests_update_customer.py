import pytest

pytestmark = [pytest.mark.django_db]


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


@pytest.fixture
def amocrm_user(user, factory):
    return factory.amocrm_user(amocrm_id=1369385)


@pytest.mark.usefixtures("_successful_response")
def test_update_customer_request_fields(amocrm_user, amocrm_client, post):
    amocrm_user.user.first_name = "First"
    amocrm_user.user.last_name = "Last"
    amocrm_user.user.tags = ["b2b", "any-purchase"]
    amocrm_user.user.save()

    got = amocrm_client.update_customer(amocrm_user)

    assert got == 1369385
    post.assert_called_once_with(
        url="/api/v4/customers",
        data={
            "id": 1369385,
            "name": "First Last",
            "_embedded": {"tags": [{"name": "b2b"}, {"name": "any-purchase"}]},
        },
    )


@pytest.mark.usefixtures("_successful_response")
def test_update_anonymous_customer(amocrm_user, amocrm_client, post):
    amocrm_user.user.first_name = ""
    amocrm_user.user.last_name = ""
    amocrm_user.user.tags = []
    amocrm_user.user.save()

    got = amocrm_client.update_customer(amocrm_user)

    assert got == 1369385
    post.assert_called_once_with(
        url="/api/v4/customers",
        data={
            "id": 1369385,
            "name": "Anonymous",
            "_embedded": {"tags": []},
        },
    )
