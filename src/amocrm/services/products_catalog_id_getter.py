from django.core.cache import cache

from app.exceptions import AppServiceException
from app.services import BaseService


class AmoCRMProductsCatalogIdGetterException(AppServiceException):
    """Raises when it's impossible to retrieve AmoCRM product catalog id"""


class AmoCRMProductsCatalogIdGetter(BaseService):
    """
    Returns AmoCRM product catalog ID
    This catalog is hardcoded in AmoCRM it's id is unique for every company
    We need to store this value to interact with list of products
    """

    def act(self) -> int:
        products_catalog = cache.get("amocrm_products_catalog_id")
        if products_catalog is not None:
            return products_catalog

        return self.set_id_to_cache()

    @staticmethod
    def set_id_to_cache() -> int:
        from amocrm.client import AmoCRMClient

        client = AmoCRMClient()
        products_catalogs = [catalog for catalog in client.get_catalogs() if catalog.type == "products"]
        if len(products_catalogs) != 0:
            product_catalog_id = products_catalogs[0].id
            cache.set("amocrm_products_catalog_id", product_catalog_id)
            return product_catalog_id

        raise AmoCRMProductsCatalogIdGetterException("Cannot retrieve amocrm_products_catalog_id")
