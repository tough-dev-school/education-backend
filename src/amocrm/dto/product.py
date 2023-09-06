from dataclasses import dataclass
from typing import Annotated, NotRequired, TypedDict

from amocrm.cache.catalog_id import get_catalog_id
from amocrm.cache.product_fields_ids import get_product_field_id
from amocrm.dto.base import AmoDTO
from products.models import Course


class ProductFieldValue(TypedDict):
    value: str  # any product's value stores as string in amo


class ProductField(TypedDict):
    field_id: int
    values: Annotated[list[ProductFieldValue], 1]  # we don't need to use more than 1 value per field


class Product(TypedDict):
    id: NotRequired[int]
    name: str
    custom_fields_values: list[ProductField]


@dataclass
class AmoCRMProduct(AmoDTO):
    course: Course

    def create(self) -> int:
        """Create product in amocrm and returns its amocrm_id"""
        response = self.http.post(
            url=f"/api/v4/catalogs/{get_catalog_id(catalog_type='products')}/elements",
            data=[self._get_course_as_product()],
        )
        return response["_embedded"]["elements"][0]["id"]

    def update(self) -> None:
        """Update product in amocrm for given course"""
        data = self._get_course_as_product()
        data.update({"id": self.course.amocrm_course.amocrm_id})

        self.http.patch(
            url=f"/api/v4/catalogs/{get_catalog_id(catalog_type='products')}/elements",
            data=[data],
        )

    def _get_course_as_product(self) -> Product:
        price = ProductField(
            field_id=get_product_field_id(field_code="PRICE"),
            values=[ProductFieldValue(value=str(self.course.price))],
        )
        slug = ProductField(
            field_id=get_product_field_id(field_code="SKU"),
            values=[ProductFieldValue(value=self.course.slug)],
        )
        unit = ProductField(
            field_id=get_product_field_id(field_code="UNIT"),
            values=[ProductFieldValue(value="шт")],  # 'piece' as unit type suits best for courses
        )
        fields_values = [price, slug, unit]

        if self.course.group is not None:
            fields_values.append(
                ProductField(
                    field_id=get_product_field_id(field_code="GROUP"),
                    values=[ProductFieldValue(value=self.course.group.slug)],
                )
            )
        return Product(
            name=self.course.name,
            custom_fields_values=fields_values,
        )
