from dataclasses import dataclass

from amocrm.cache.products_catalog_id_getter import AmoCRMProductsCatalogIdGetter
from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMServiceException
from amocrm.models import AmoCRMCourse
from amocrm.services.product_catalog_fields_ids_manager import AmoCRMProductCatalogFieldsIdsManager
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
    """

    amocrm_course: AmoCRMCourse

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()
        self.course = self.amocrm_course.course

    def act(self) -> None:
        course_as_element = AmoCRMCatalogElement(
            id=self.amocrm_course.amocrm_id,
            name=self.course.name,
            custom_fields_values=self.get_fields_values(),
        )

        self.client.update_catalog_element(
            catalog_id=self.product_catalog_id,
            element=course_as_element,
        )

    def get_fields_values(self) -> list[AmoCRMCatalogElementField]:
        price_field = AmoCRMCatalogElementField(
            field_id=self.price_field_id,
            values=[AmoCRMCatalogElementFieldValue(value=self.course.price)],
        )
        sku_field = AmoCRMCatalogElementField(
            field_id=self.sku_field_id,
            values=[AmoCRMCatalogElementFieldValue(value=self.course.slug)],
        )
        fields_values = [price_field, sku_field]

        if self.course.group is not None:
            group_field = AmoCRMCatalogElementField(
                field_id=self.sku_field_id,
                values=[AmoCRMCatalogElementFieldValue(value=self.course.group.slug)],
            )
            fields_values.append(group_field)
        return fields_values

    @property
    def group_field_id(self) -> int:
        return AmoCRMProductCatalogFieldsIdsManager().get_product_field_id("GROUP")

    @property
    def sku_field_id(self) -> int:
        return AmoCRMProductCatalogFieldsIdsManager().get_product_field_id("SKU")

    @property
    def price_field_id(self) -> int:
        return AmoCRMProductCatalogFieldsIdsManager().get_product_field_id("PRICE")

    @property
    def product_catalog_id(self) -> int:
        return AmoCRMProductsCatalogIdGetter()()
