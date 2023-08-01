from dataclasses import dataclass

from amocrm.client import AmoCRMClient
from amocrm.models import AmoCRMCourse
from amocrm.services.product_catalog_fields_manager import AmoCRMProductCatalogFieldsManager
from amocrm.services.products_catalog_getter import AmoCRMSProductsCatalogGetter
from amocrm.types import AmoCRMCatalogElement
from amocrm.types import AmoCRMCatalogElementField
from amocrm.types import AmoCRMCatalogElementFieldValue
from app.exceptions import AppServiceException
from app.services import BaseService


class AmoCRMCourseUpdaterException(AppServiceException):
    """Raises when it's impossible to update amocrm course"""


@dataclass
class AmoCRMCourseUpdater(BaseService):
    """
    Creates course as element of products catalog in amocrm
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
        return AmoCRMProductCatalogFieldsManager().get_product_field("GROUP").id

    @property
    def sku_field_id(self) -> int:
        return AmoCRMProductCatalogFieldsManager().get_product_field("SKU").id

    @property
    def price_field_id(self) -> int:
        return AmoCRMProductCatalogFieldsManager().get_product_field("PRICE").id

    @property
    def product_catalog_id(self) -> int:
        return AmoCRMSProductsCatalogGetter()().id
