import pytest


@pytest.fixture(autouse=True)
def _mock_contact_field_id(mocker):
    mocker.patch("amocrm.dto.customer.get_contact_field_id", return_value=2235143)


@pytest.fixture
def user(user):
    user.email = "dada@da.net"
    user.first_name = "First"
    user.last_name = "Last"
    user.tags = ["b2b", "any-purchase"]
    user.save()
    return user


@pytest.fixture
def post(mocker):
    return mocker.patch("amocrm.client.http.AmoCRMHTTP.post")


@pytest.fixture
def patch(mocker):
    return mocker.patch("amocrm.client.http.AmoCRMHTTP.patch")
