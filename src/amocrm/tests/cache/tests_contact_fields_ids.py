import pytest

from django.core.cache import cache

from amocrm.cache.contact_fields_ids import get_contact_field_id
from amocrm.exceptions import AmoCRMCacheException
from amocrm.types import AmoCRMCatalogField

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def email_field():
    return AmoCRMCatalogField(
        id=333,
        name="Email",
        type="multitext",
        code="EMAIL",
        nested=None,
    )


@pytest.fixture
def fields(email_field):
    return [email_field, AmoCRMCatalogField(id=123, name="Телефон", type="multitext", code="PHONE")]


@pytest.fixture
def mock_get_contact_fields(mocker, fields):
    return mocker.patch("amocrm.client.AmoCRMClient.get_contact_fields", return_value=fields)


def test_return_id_if_in_cache(mock_get_contact_fields):
    cache.set("amocrm_contacts_email_id", 333)

    got = get_contact_field_id("EMAIL")

    assert got == 333
    mock_get_contact_fields.assert_not_called()


def test_return_field_from_response_if_not_in_cache(mock_get_contact_fields):
    cache.clear()

    got = get_contact_field_id("EMAIL")

    assert got == 333
    assert cache.get("amocrm_contacts_email_id") == 333
    mock_get_contact_fields.assert_called_once()


def test_fail_if_not_in_cache_and_not_in_response(mock_get_contact_fields):
    cache.clear()
    mock_get_contact_fields.return_value = [AmoCRMCatalogField(id=123, name="Телефон", type="multitext", code="PHONE")]

    with pytest.raises(AmoCRMCacheException):
        get_contact_field_id("EMAIL")
