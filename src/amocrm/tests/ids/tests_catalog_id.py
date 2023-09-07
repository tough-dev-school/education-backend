import pytest

from amocrm.exceptions import AmoCRMCacheException
from amocrm.ids import products_catalog_id


@pytest.fixture
def products_catalog():
    return dict(id=333, name="Products", type="products")


@pytest.fixture
def catalogs(products_catalog):
    return [products_catalog, dict(id=123, name="Useless", type="meh")]


@pytest.fixture(autouse=True)
def mock_get_catalogs(mocker, catalogs):
    return mocker.patch("amocrm.dto.catalogs.AmoCRMCatalogs.get", return_value=catalogs)


def test_return_catalog_id(products_catalog):
    got = products_catalog_id()

    assert got == products_catalog["id"]


def test_fail_if_no_products_catalog(mock_get_catalogs):
    mock_get_catalogs.return_value = [dict(id=111, name="NotWhatINeed", type="sad-story")]

    with pytest.raises(AmoCRMCacheException):
        products_catalog_id()
