from dataclasses import dataclass

from django.db.models import QuerySet

from amocrm.cache.catalog_id import get_catalog_id
from amocrm.cache.product_fields_ids import get_product_field_id
from amocrm.dto.base import AmoDTO
from products.models import Group


@dataclass
class AmoCRMGroup(AmoDTO):
    """
    Product group is just a ENUM field for Product in amocrm
    This DTO creates and updates product groups with single request
    """

    groups: QuerySet[Group]

    def push(self) -> dict[str, int]:
        """
        Updates product catalog field
        returns list of pairs of group_slug: amocrm_id
        """
        response = self.http.patch(
            url=f"/api/v4/catalogs/{get_catalog_id(catalog_type='products')}/custom_fields",
            data=[
                {
                    "id": get_product_field_id(field_code="GROUP"),
                    "nested": self._get_groups_as_product_field(),
                }
            ],
        )
        updated_fields = response["_embedded"]["custom_fields"][0]["nested"]
        return {group_field["value"]: group_field["id"] for group_field in updated_fields}

    def _get_groups_as_product_field(self) -> list[dict]:
        groups_as_field = []
        for group in self.groups:
            if hasattr(group, "amocrm_group"):
                groups_as_field.append({"id": group.amocrm_group.amocrm_id, "value": group.slug})
            else:
                groups_as_field.append({"value": group.slug})

        return groups_as_field
