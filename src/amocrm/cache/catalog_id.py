from typing import Literal

from django.core.cache import cache

from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMCacheException

CATALOG_TYPES = Literal["products"]
CATALOGS_TO_CACHE = {"products": "amocrm_products_catalog_id"}


def get_catalog_id_amocrm(catalog_type: CATALOG_TYPES) -> int:
    client = AmoCRMClient()
    catalogs = [catalog for catalog in client.get_catalogs() if catalog.type == catalog_type]
    if len(catalogs) != 1:
        raise AmoCRMCacheException(f"Cannot retrieve {catalog_type} catalog id")

    return catalogs[0].id


def get_catalog_id(catalog_type: CATALOG_TYPES) -> int:
    cache_key = CATALOGS_TO_CACHE[catalog_type]
    return cache.get_or_set(cache_key, lambda: get_catalog_id_amocrm(catalog_type), timeout=None)  # type: ignore


__all__ = ["get_catalog_id"]
