from dataclasses import dataclass
from typing import Iterable

from amocrm.client import http
from products.models import Group


@dataclass
class AmoCRMGroups:
    """
    Product group is just a ENUM field for Product in amocrm
    This DTO creates and updates product groups with single request
    """

    groups: Iterable[Group]

    def push(self) -> list[tuple[str, int]]:
        """
        Updates product catalog field
        returns list of pairs like [(group_slug, amocrm_id), ...]
        """
        from amocrm.ids import product_field_id
        from amocrm.ids import products_catalog_id

        groups_as_product_fields = [self._get_group_as_product_field(group=group) for group in self.groups]
        response = http.patch(
            url=f"/api/v4/catalogs/{products_catalog_id()}/custom_fields",
            data=[
                {
                    "id": product_field_id(field_code="GROUP"),
                    "nested": groups_as_product_fields,
                }
            ],
        )
        updated_fields = response["_embedded"]["custom_fields"][0]["nested"]
        return [(group_field["value"], group_field["id"]) for group_field in updated_fields]

    @staticmethod
    def _get_group_as_product_field(group: Group) -> dict[str, str | int]:
        data: dict[str, str | int] = {"value": group.slug}
        if hasattr(group, "amocrm_group"):
            data.update({"id": group.amocrm_group.amocrm_id})
        return data
