import pytest

from amocrm.types import AmoCRMElementField
from amocrm.types import AmoCRMElementFieldValue


@pytest.fixture
def course(factory):
    group = factory.group(slug="top-group")
    return factory.course(name="TopCourse", slug="top-course", price=99, group=group)


@pytest.fixture
def element_fields():
    price_value = AmoCRMElementFieldValue(value=99)
    sku_value = AmoCRMElementFieldValue(value="top-course")
    group_value = AmoCRMElementFieldValue(value="top-group")
    unit_value = AmoCRMElementFieldValue(value="шт")
    return [
        AmoCRMElementField(field_id=333, values=[price_value]),
        AmoCRMElementField(field_id=333, values=[sku_value]),
        AmoCRMElementField(field_id=333, values=[unit_value]),
        AmoCRMElementField(field_id=333, values=[group_value]),
    ]
