import pytest


@pytest.fixture(autouse=True)
def _mock_cached_fields_id(mocker):
    mocker.patch("amocrm.dto.customer.get_contact_field_id", return_value=2235143)
    mocker.patch("amocrm.dto.lead.get_catalog_id", return_value=777)
    mocker.patch("amocrm.dto.lead.get_b2c_pipeline_id", return_value=555)
    mocker.patch("amocrm.dto.lead.get_b2c_pipeline_status_id", return_value=333)


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
