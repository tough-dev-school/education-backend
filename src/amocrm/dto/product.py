from dataclasses import dataclass

from amocrm.cache.catalog_id import get_catalog_id
from amocrm.cache.product_fields_ids import get_product_field_id
from amocrm.dto.base import AmoDTO
from products.models import Course


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

    def _get_course_as_product(self) -> dict:
        price_field = {
            "field_id": get_product_field_id(field_code="PRICE"),
            "values": [{"value": str(self.course.price)}],  # it's stored as string in amo
        }
        slug_field = {
            "field_id": get_product_field_id(field_code="SKU"),
            "values": [{"value": self.course.slug}],
        }
        unit_field = {
            "field_id": get_product_field_id(field_code="UNIT"),
            "values": [{"value": "шт"}],  # 'piece' as unit type suits best for courses
        }
        fields_values = [price_field, slug_field, unit_field]

        if self.course.group is not None:
            fields_values.append(
                {
                    "field_id": get_product_field_id(field_code="GROUP"),
                    "values": [{"value": self.course.group.slug}],
                }
            )

        return {
            "name": self.course.name,
            "custom_fields_values": fields_values,
        }
