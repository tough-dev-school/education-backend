from typing import Literal

from django.core.cache import cache

from amocrm.services.products_catalog_getter import AmoCRMSProductsCatalogGetter
from amocrm.types import AmoCRMCatalogField
from app.exceptions import AppServiceException

FIELDS_CODES_LITERAL = Literal["SKU", "PRICE", "SPECIAL_PRICE_1", "GROUP", "DESCRIPTION", "EXTERNAL_ID"]
FIELDS_CODES = ["SKU", "PRICE", "SPECIAL_PRICE_1", "GROUP", "DESCRIPTION", "EXTERNAL_ID"]
FIELDS_TO_CACHE = {
    "SKU": "amocrm_products_sku",
    "PRICE": "amocrm_products_price",
    "SPECIAL_PRICE_1": "amocrm_products_special_price_1",
    "GROUP": "amocrm_products_group",
    "DESCRIPTION": "amocrm_products_description",
    "EXTERNAL_ID": "amocrm_products_external_id",
}


class AmoCRMProductCatalogFieldsManagerException(AppServiceException):
    """Raises when it's impossible to retrieve AmoCRM products field"""


class AmoCRMProductCatalogFieldsManager:
    """
    Returns AmoCRMCatalogField for chosen field code

    AmoCRM replace fields even with same values,
    so we need to store fields ids and values to
    be able to safely update or create product fields
    """

    def get_product_field(self, field_code: FIELDS_CODES_LITERAL) -> AmoCRMCatalogField:
        cache_key = FIELDS_TO_CACHE[field_code]
        amocrm_field = cache.get(cache_key)
        if amocrm_field is not None:
            return amocrm_field

        return self._set_product_fields_to_cache(field_code)

    def _set_product_fields_to_cache(self, field_code: FIELDS_CODES_LITERAL) -> AmoCRMCatalogField:
        from amocrm.client import AmoCRMClient

        client = AmoCRMClient()
        product_fields = [field for field in client.get_catalog_fields(self._product_catalog_id) if field.code in FIELDS_CODES]
        for product_field in product_fields:
            self._set_product_field_to_cache(field=product_field)

        chosen_field = [field for field in product_fields if field.code == field_code]
        if len(chosen_field) == 1:
            return chosen_field[0]

        raise AmoCRMProductCatalogFieldsManagerException(f"Cannot retrieve {field_code} product field")

    @staticmethod
    def _set_product_field_to_cache(field: AmoCRMCatalogField) -> None:
        cache_key = FIELDS_TO_CACHE[field.code]
        cache.set(cache_key, field)

    @property
    def _product_catalog_id(self) -> int:
        return AmoCRMSProductsCatalogGetter()().id
