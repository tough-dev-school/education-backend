import typing

from amocrm.dto.catalogs import AmoCRMCatalogs
from amocrm.exceptions import AmoCRMCacheException
from amocrm.ids.catalog_id import get_catalog_id

FIELDS_CODES = typing.Literal["SKU", "PRICE", "SPECIAL_PRICE_1", "GROUP", "DESCRIPTION", "EXTERNAL_ID", "UNIT"]


def get_product_field_id(field_code: FIELDS_CODES) -> int:
    product_catalog_id = get_catalog_id(catalog_type="products")

    product_fields = [field for field in AmoCRMCatalogs.get_fields(catalog_id=product_catalog_id) if field["code"] == field_code]
    if len(product_fields) != 1:
        raise AmoCRMCacheException(f"Cannot retrieve {field_code} product field")

    return product_fields[0]["id"]
