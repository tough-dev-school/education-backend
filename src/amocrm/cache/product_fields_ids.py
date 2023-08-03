import typing

from django.core.cache import cache

from amocrm.cache.catalog_id import get_catalog_id
from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMCacheException

FIELDS_CODES = typing.Literal["SKU", "PRICE", "SPECIAL_PRICE_1", "GROUP", "DESCRIPTION", "EXTERNAL_ID", "UNIT"]
FIELDS_TO_CACHE = {
    "SKU": "amocrm_products_sku_id",
    "PRICE": "amocrm_products_price_id",
    "SPECIAL_PRICE_1": "amocrm_products_special_price_1_id",
    "GROUP": "amocrm_products_group_id",
    "DESCRIPTION": "amocrm_products_description_id",
    "EXTERNAL_ID": "amocrm_products_external_id_id",
    "UNIT": "amocrm_products_unit_id",
}


def get_field_id_from_amocrm(field_code: FIELDS_CODES) -> int:
    client = AmoCRMClient()
    product_catalog_id = get_catalog_id(catalog_type="products")

    product_fields = [field for field in client.get_catalog_fields(product_catalog_id) if field.code == field_code]
    if len(product_fields) != 1:
        raise AmoCRMCacheException(f"Cannot retrieve {field_code} product field")

    return product_fields[0].id


def get_product_field_id(field_code: FIELDS_CODES) -> int:
    cache_key = FIELDS_TO_CACHE[field_code]
    return cache.get_or_set(cache_key, lambda: get_field_id_from_amocrm(field_code), timeout=None)  # type: ignore


__all__ = ["get_product_field_id"]
