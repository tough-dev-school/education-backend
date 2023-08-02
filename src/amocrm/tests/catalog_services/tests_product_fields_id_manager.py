import pytest

from django.core.cache import cache

from amocrm.services.product_catalog_fields_ids_manager import AmoCRMProductCatalogFieldsIdsManager
from amocrm.services.product_catalog_fields_ids_manager import AmoCRMProductCatalogFieldsIdsManagerException
from amocrm.types import AmoCRMCatalogField
from amocrm.types import AmoCRMCatalogFieldValue

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def mock_product_catalog_getter(mocker):
    return mocker.patch("amocrm.services.products_catalog_id_getter.AmoCRMProductsCatalogIdGetter.__call__", return_value=123)


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


@pytest.fixture
def get_product_field_id():
    return lambda field_code: AmoCRMProductCatalogFieldsIdsManager().get_product_field_id(field_code)


def test_return_id_if_in_cache(get_product_field_id, mock_get_catalog_fields):
    cache.set("amocrm_products_group_id", 333)

    got = get_product_field_id("GROUP")

    assert got == 333
    mock_get_catalog_fields.assert_not_called()


@pytest.mark.usefixtures("mock_product_catalog_getter")
def test_return_field_from_response_if_not_in_cache(get_product_field_id, mock_get_catalog_fields):
    cache.set("amocrm_products_group_id", None)

    got = get_product_field_id("GROUP")

    assert got == 333
    assert cache.get("amocrm_products_group_id") == 333
    mock_get_catalog_fields.assert_called_once()


@pytest.mark.usefixtures("mock_product_catalog_getter")
def test_fail_if_not_in_cache_and_not_in_response(get_product_field_id, mock_get_catalog_fields):
    cache.set("amocrm_products_group_id", None)
    mock_get_catalog_fields.return_value = [AmoCRMCatalogField(id=123, name="Наш айдишник", type="text", code="EXTERNAL_ID")]

    with pytest.raises(AmoCRMProductCatalogFieldsIdsManagerException):
        get_product_field_id("GROUP")
