import pytest

from amocrm.types import AmoCRMCatalogElementField
from amocrm.types import AmoCRMCatalogElementFieldValue
from amocrm.types import AmoCRMCatalogField


@pytest.fixture(autouse=True)
def _mock_fields_id(mocker):
    mocker.patch(
        "amocrm.services.product_catalog_fields_manager.AmoCRMProductCatalogFieldsManager.get_product_field",
        return_value=AmoCRMCatalogField(id=333, name="aa", type="bb", code="EVERYTHING"),
    )
    mocker.patch("amocrm.services.products_catalog_getter.AmoCRMProductsCatalogIdGetter.__call__", return_value=777)


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
