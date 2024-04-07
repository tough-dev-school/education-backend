import pytest

from apps.amocrm import types
from apps.amocrm.exceptions import AmoCRMCacheException
from apps.amocrm.ids import product_field_id


@pytest.fixture(autouse=True)
def mock_get_catalog_id(mocker):
    return mocker.patch("apps.amocrm.ids.products_catalog_id", return_value=123)


@pytest.fixture
def group_field():
    return types.CatalogField(id=333, code="GROUP")


@pytest.fixture
def fields(group_field):
    return [
        group_field,
        types.CatalogField(id=123, code="EXTERNAL_ID"),
    ]


@pytest.fixture(autouse=True)
def mock_get_catalog_fields(mocker, fields):
    return mocker.patch("apps.amocrm.dto.catalogs.AmoCRMCatalogsDTO.get_fields", return_value=fields)


def test_return_id_if_in_cache(group_field):
    got = product_field_id("GROUP")

    assert got == group_field.id


def test_fail_if_not_in_cache_and_not_in_response(mock_get_catalog_fields):
    mock_get_catalog_fields.return_value = [types.CatalogField(id=123, code="EXTERNAL_ID")]

    with pytest.raises(AmoCRMCacheException):
        product_field_id("GROUP")
