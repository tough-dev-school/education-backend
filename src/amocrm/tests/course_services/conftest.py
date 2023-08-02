import pytest

from amocrm.types import AmoCRMCatalogElementField
from amocrm.types import AmoCRMCatalogElementFieldValue


@pytest.fixture(autouse=True)
def _mock_fields_id(mocker):
    mocker.patch(
        "amocrm.services.product_catalog_fields_ids_manager.AmoCRMProductCatalogFieldsIdsManager.get_product_field_id",
        return_value=333,
    )
    mocker.patch("amocrm.services.products_catalog_id_getter.AmoCRMProductsCatalogIdGetter.__call__", return_value=777)


@pytest.fixture
def course(factory):
    group = factory.group(slug="top-group")
    return factory.course(name="TopCourse", slug="top-course", price=99, group=group)


@pytest.fixture
def element_fields():
    price_value = AmoCRMCatalogElementFieldValue(value=99)
    sku_value = AmoCRMCatalogElementFieldValue(value="top-course")
    group_value = AmoCRMCatalogElementFieldValue(value="top-group")
    return [
        AmoCRMCatalogElementField(field_id=333, values=[price_value]),
        AmoCRMCatalogElementField(field_id=333, values=[sku_value]),
        AmoCRMCatalogElementField(field_id=333, values=[group_value]),
    ]
