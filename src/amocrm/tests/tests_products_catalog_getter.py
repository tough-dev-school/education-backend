import pytest

from django.core.cache import cache

from amocrm.services import AmoCRMSProductsCatalogGetter
from amocrm.services.amocrm_products_catalog_getter import AmoCRMSProductsCatalogGetterException
from amocrm.types import AmoCRMCatalogField

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def products_catalog():
    return AmoCRMCatalogField(id=333, name="Products", type="products")


@pytest.fixture
def catalogs(products_catalog):
    return [products_catalog, AmoCRMCatalogField(id=123, name="Useless", type="meh")]


@pytest.fixture(autouse=True)
def mock_get_catalogs(mocker, catalogs):
    return mocker.patch("amocrm.client.AmoCRMClient.get_catalogs", return_value=catalogs)


@pytest.fixture
def products_catalog_getter():
    return AmoCRMSProductsCatalogGetter()


def test_return_catalog_if_in_cache(products_catalog_getter, products_catalog, mock_get_catalogs):
    cache.set("amocrm_products_catalog", products_catalog)

    got = products_catalog_getter()

    assert got == products_catalog
    mock_get_catalogs.assert_not_called()


def test_return_catalog_from_response_if_not_in_cache(products_catalog_getter, products_catalog, mock_get_catalogs):
    cache.set("amocrm_products_catalog", None)

    got = products_catalog_getter()

    assert got == products_catalog
    assert cache.get("amocrm_products_catalog") == products_catalog
    mock_get_catalogs.assert_called_once()


def test_fail_if_not_in_cache_and_not_in_response(products_catalog_getter, products_catalog, mock_get_catalogs):
    cache.set("amocrm_products_catalog", None)
    mock_get_catalogs.return_value = [AmoCRMCatalogField(id=111, name="NotWhatINeed", type="sad-story")]

    with pytest.raises(AmoCRMSProductsCatalogGetterException):
        products_catalog_getter()
