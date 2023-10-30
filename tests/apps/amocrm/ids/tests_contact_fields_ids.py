import pytest

from apps.amocrm.exceptions import AmoCRMCacheException
from apps.amocrm.ids import contact_field_id


@pytest.fixture
def email_field():
    return dict(
        id=333,
        code="EMAIL",
    )


@pytest.fixture
def fields(email_field):
    return [email_field, dict(id=123, code="PHONE")]


@pytest.fixture(autouse=True)
def mock_get_contact_fields(mocker, fields):
    return mocker.patch("apps.amocrm.dto.catalogs.AmoCRMCatalogs.get_contacts_fields", return_value=fields)


def test_return_field_id(email_field):
    got = contact_field_id("EMAIL")

    assert got == email_field["id"]


def test_fail_if_not_in_cache_and_not_in_response(mock_get_contact_fields):
    mock_get_contact_fields.return_value = [dict(id=123, code="PHONE")]

    with pytest.raises(AmoCRMCacheException):
        contact_field_id("EMAIL")
