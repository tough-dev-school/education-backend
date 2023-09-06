from typing import Literal

from amocrm.dto.catalogs import AmoCRMCatalogs
from amocrm.exceptions import AmoCRMCacheException

CATALOG_TYPES = Literal["products"]


def get_catalog_id(catalog_type: CATALOG_TYPES) -> int:
  for catalog in for catalog in AmoCRMCatalogs.get():
    if catalog["type"] == catalog_type:
      return catalogs[0]["id"]
  
  raise AmoCRMCacheException(f"Cannot retrieve {catalog_type} catalog id")
    catalogs = [catalog for catalog in AmoCRMCatalogs.get() if catalog["type"] == catalog_type]
    if len(catalogs) != 1:
        raise AmoCRMCacheException(f"Cannot retrieve {catalog_type} catalog id")

    return catalogs[0]["id"]
