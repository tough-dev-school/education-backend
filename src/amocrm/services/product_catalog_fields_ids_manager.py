import typing

from django.core.cache import cache

from amocrm.services.products_catalog_id_getter import AmoCRMProductsCatalogIdGetter
from amocrm.types import AmoCRMCatalogField
from app.exceptions import AppServiceException

FIELDS_CODES_LITERAL = typing.Literal["SKU", "PRICE", "SPECIAL_PRICE_1", "GROUP", "DESCRIPTION", "EXTERNAL_ID"]
FIELDS_CODES = set(typing.get_args(FIELDS_CODES_LITERAL))
FIELDS_TO_CACHE = {
    "SKU": "amocrm_products_sku_id",
    "PRICE": "amocrm_products_price_id",
    "SPECIAL_PRICE_1": "amocrm_products_special_price_1_id",
    "GROUP": "amocrm_products_group_id",
    "DESCRIPTION": "amocrm_products_description_id",
    "EXTERNAL_ID": "amocrm_products_external_id_id",
}


class AmoCRMProductCatalogFieldsIdsManagerException(AppServiceException):
    """Raises when it's impossible to retrieve AmoCRM products field id"""


class AmoCRMProductCatalogFieldsIdsManager:
    """
    Returns AmoCRMCatalogField id for chosen field code

    AmoCRM replace fields even with same values,
    so we need to store fields ids to be able
    to safely update or create product fields
    """

    def get_product_field_id(self, field_code: FIELDS_CODES_LITERAL) -> int:
        cache_key = FIELDS_TO_CACHE[field_code]
        amocrm_field = cache.get(cache_key)
        if amocrm_field is not None:
            return amocrm_field

        return self._set_product_fields_id_to_cache(field_code)

    def _set_product_fields_id_to_cache(self, field_code: FIELDS_CODES_LITERAL) -> int:
        from amocrm.client import AmoCRMClient

        client = AmoCRMClient()
        product_fields = [field for field in client.get_catalog_fields(self._product_catalog_id) if field.code in FIELDS_CODES]
        for product_field in product_fields:
            self._set_product_field_id_to_cache(field=product_field)

        chosen_field = [field for field in product_fields if field.code == field_code]
        if len(chosen_field) == 1:
            return chosen_field[0].id

        raise AmoCRMProductCatalogFieldsIdsManagerException(f"Cannot retrieve {field_code} product field")

    @staticmethod
    def _set_product_field_id_to_cache(field: AmoCRMCatalogField) -> None:
        cache_key = FIELDS_TO_CACHE[field.code]
        cache.set(cache_key, field.id)

    @property
    def _product_catalog_id(self) -> int:
        return AmoCRMProductsCatalogIdGetter()()
