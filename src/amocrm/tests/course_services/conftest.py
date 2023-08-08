import pytest

from amocrm.types import AmoCRMCatalogElementField
from amocrm.types import AmoCRMCatalogElementFieldValue


@pytest.fixture
def course(factory):
    group = factory.group(slug="top-group")
    return factory.course(name="TopCourse", slug="top-course", price=99, group=group)


@pytest.fixture
def element_fields():
    price_value = AmoCRMCatalogElementFieldValue(value=99)
    sku_value = AmoCRMCatalogElementFieldValue(value="top-course")
    group_value = AmoCRMCatalogElementFieldValue(value="top-group")
    unit_value = AmoCRMCatalogElementFieldValue(value="шт")
    return [
        AmoCRMCatalogElementField(field_id=333, values=[price_value]),
        AmoCRMCatalogElementField(field_id=333, values=[sku_value]),
        AmoCRMCatalogElementField(field_id=333, values=[unit_value]),
        AmoCRMCatalogElementField(field_id=333, values=[group_value]),
    ]
