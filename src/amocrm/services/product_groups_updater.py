from amocrm.client import AmoCRMClient
from amocrm.models import AmoCRMProductGroup
from amocrm.services.product_catalog_fields_manager import AmoCRMProductCatalogFieldsManager
from amocrm.services.products_catalog_getter import AmoCRMSProductsCatalogGetter
from amocrm.types import AmoCRMCatalogFieldValue
from app.services import BaseService
from products.models import Group


class AmoCRMProductGroupsUpdater(BaseService):
    """
    Updates list of options in product catalog group field
    It's necessary to save amocrm_id for ProductGroups and send these ids too,
    if not - next updating will set new field options with new ids but same values
    """

    def __init__(self) -> None:
        self.client = AmoCRMClient()

    def act(self) -> None:
        groups_as_field_values = self.get_all_groups_as_field_values()
        groups_with_amocrm_ids = self.client.update_catalog_field(
            catalog_id=self.product_catalog_id,
            field_id=self.group_field_id,
            field_values=groups_as_field_values,
        )

        self.save_amocrm_product_groups(groups_with_amocrm_ids=groups_with_amocrm_ids)

    @staticmethod
    def get_all_groups_as_field_values() -> list[AmoCRMCatalogFieldValue]:
        groups = Group.objects.all()
        groups_as_field_values = []
        for group in groups:
            if hasattr(group, "amocrm_group"):
                groups_as_field_values.append(AmoCRMCatalogFieldValue(id=group.amocrm_group.amocrm_id, value=group.slug))
            else:
                groups_as_field_values.append(AmoCRMCatalogFieldValue(value=group.slug))
        return groups_as_field_values

    @staticmethod
    def save_amocrm_product_groups(groups_with_amocrm_ids: list[AmoCRMCatalogFieldValue]) -> None:
        for group_with_amocrm_id in groups_with_amocrm_ids:
            group = Group.objects.get(slug=group_with_amocrm_id.value)
            if not hasattr(group, "amocrm_group"):
                AmoCRMProductGroup.objects.create(group=group, amocrm_id=group_with_amocrm_id.id)  # type: ignore

    @property
    def product_catalog_id(self) -> int:
        return AmoCRMSProductsCatalogGetter()().id

    @property
    def group_field_id(self) -> int:
        return AmoCRMProductCatalogFieldsManager().get_product_field("GROUP").id
