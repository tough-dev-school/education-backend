from dataclasses import dataclass

from amocrm.cache.catalog_id import get_catalog_id
from amocrm.cache.product_fields_ids import get_product_field_id
from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMServiceException
from amocrm.models import AmoCRMCourse
from amocrm.types import AmoCRMCatalogElement
from amocrm.types import AmoCRMCatalogElementField
from amocrm.types import AmoCRMCatalogElementFieldValue
from app.services import BaseService


class AmoCRMCourseUpdaterException(AmoCRMServiceException):
    """Raises when it's impossible to update amocrm course"""


@dataclass
class AmoCRMCourseUpdater(BaseService):
    """
    Updates course as element of products catalog in amocrm
    Returns id of updated AmoCRM product catalog entity
    """

    amocrm_course: AmoCRMCourse

    unit = "шт"  # hardcoded unit type for all courses

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()
        self.course = self.amocrm_course.course

    def act(self) -> int:
        course_as_element = AmoCRMCatalogElement(
            id=self.amocrm_course.amocrm_id,
            name=self.course.name,
            custom_fields_values=self.get_fields_values(),
        )

        self.client.update_catalog_element(
            catalog_id=self.product_catalog_id,
            element=course_as_element,
        )

        return self.amocrm_course.amocrm_id

    def get_fields_values(self) -> list[AmoCRMCatalogElementField]:
        price_field = AmoCRMCatalogElementField(
            field_id=self.price_field_id,
            values=[AmoCRMCatalogElementFieldValue(value=self.course.price)],
        )
        sku_field = AmoCRMCatalogElementField(
            field_id=self.sku_field_id,
            values=[AmoCRMCatalogElementFieldValue(value=self.course.slug)],
        )
        unit_field = AmoCRMCatalogElementField(
            field_id=self.unit_field_id,
            values=[AmoCRMCatalogElementFieldValue(value=self.unit)],
        )
        fields_values = [price_field, sku_field, unit_field]

        if self.course.group is not None:
            group_field = AmoCRMCatalogElementField(
                field_id=self.group_field_id,
                values=[AmoCRMCatalogElementFieldValue(value=self.course.group.slug)],
            )
            fields_values.append(group_field)
        return fields_values

    @property
    def sku_field_id(self) -> int:
        return get_product_field_id(field_code="SKU")

    @property
    def price_field_id(self) -> int:
        return get_product_field_id(field_code="PRICE")

    @property
    def group_field_id(self) -> int:
        return get_product_field_id(field_code="GROUP")

    @property
    def unit_field_id(self) -> int:
        return get_product_field_id(field_code="UNIT")

    @property
    def product_catalog_id(self) -> int:
        return get_catalog_id(catalog_type="products")
