import pytest

from django.core.cache import cache

from amocrm.cache.product_fields_ids import get_product_field_id
from amocrm.exceptions import AmoCRMCacheException
from amocrm.types import AmoCRMCatalogField
from amocrm.types import AmoCRMCatalogFieldValue

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def mock_get_catalog_id(mocker):
    return mocker.patch("amocrm.cache.product_fields_ids.get_catalog_id", return_value=123)


@pytest.fixture
def group_field():
    return AmoCRMCatalogField(
        id=333,
        name="Группа",
        type="category",
        code="GROUP",
        nested=[AmoCRMCatalogFieldValue(id=555, value="popug")],
    )


@pytest.fixture
def fields(group_field):
    return [group_field, AmoCRMCatalogField(id=123, name="Наш айдишник", type="text", code="EXTERNAL_ID")]


@pytest.fixture
def mock_get_catalog_fields(mocker, fields):
    return mocker.patch("amocrm.client.AmoCRMClient.get_catalog_fields", return_value=fields)


def test_return_id_if_in_cache(mock_get_catalog_fields):
    cache.set("amocrm_products_group_id", 333)

    got = get_product_field_id("GROUP")

    assert got == 333
    mock_get_catalog_fields.assert_not_called()


@pytest.mark.usefixtures("mock_get_catalog_id")
def test_return_field_from_response_if_not_in_cache(mock_get_catalog_fields, mock_get_catalog_id):
    got = get_product_field_id("GROUP")
    mock_get_catalog_id.assert_called_once()
    assert got == 333
    assert cache.get("amocrm_products_group_id") == 333
    mock_get_catalog_fields.assert_called_once()


@pytest.mark.usefixtures("mock_get_catalog_id")
def test_fail_if_not_in_cache_and_not_in_response(mock_get_catalog_fields):
    cache.clear()
    mock_get_catalog_fields.return_value = [AmoCRMCatalogField(id=123, name="Наш айдишник", type="text", code="EXTERNAL_ID")]

    with pytest.raises(AmoCRMCacheException):
        get_product_field_id("GROUP")
