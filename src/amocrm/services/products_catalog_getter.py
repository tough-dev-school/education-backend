from django.core.cache import cache

from amocrm.types import AmoCRMCatalog
from app.exceptions import AppServiceException
from app.services import BaseService


class AmoCRMSProductsCatalogGetterException(AppServiceException):
    """Raises when it's impossible to retrieve AmoCRM structure"""


class AmoCRMSProductsCatalogGetter(BaseService):
    """
    Returns AmoCRMCatalogField for Products catalog
    This catalog is hardcoded in AmoCRM it's id is unique for every company
    We need to store this value to interact with list of products
    """

    def act(self) -> AmoCRMCatalog:
        products_catalog = cache.get("amocrm_products_catalog")
        if products_catalog is not None:
            return products_catalog

        return self.set_properties_to_cache()

    def set_properties_to_cache(self) -> AmoCRMCatalog:
        from amocrm.client import AmoCRMClient

        client = AmoCRMClient()
        products_catalogs = [catalog for catalog in client.get_catalogs() if catalog.type == "products"]
        if len(products_catalogs) != 0:
            cache.set("amocrm_products_catalog", products_catalogs[0])
            return products_catalogs[0]

        raise AmoCRMSProductsCatalogGetterException("Cannot retrieve amocrm_products_catalog")
