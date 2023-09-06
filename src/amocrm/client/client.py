from amocrm.client.http import AmoCRMHTTP
from amocrm.types import AmoCRMCatalog
from amocrm.types import AmoCRMCatalogField
from amocrm.types import AmoCRMPipeline


class AmoCRMClient:
    """
    Client to deal with amoCRM with auto tokens refresh.
    """

    def __init__(self) -> None:
        self.http: AmoCRMHTTP = AmoCRMHTTP()

    def get_contact_fields(self) -> list[AmoCRMCatalogField]:
        """Returns contacts fields"""
        response = self.http.get(url="/api/v4/contacts/custom_fields", params={"limit": 250})  # request max amount of fields
        return [AmoCRMCatalogField.from_json(contact) for contact in response["_embedded"]["custom_fields"]]

    def enable_customers(self) -> None:
        """Enable customers list is required to create/update customers"""
        self.http.patch(url="/api/v4/customers/mode", data={"mode": "segments", "is_enabled": True})

    def get_catalogs(self) -> list[AmoCRMCatalog]:
        """Returns all catalogs from amocrm"""
        response = self.http.get(url="/api/v4/catalogs", params={"limit": 250})  # request max amount of catalogs
        return [AmoCRMCatalog.from_json(catalog) for catalog in response["_embedded"]["catalogs"]]

    def get_catalog_fields(self, catalog_id: int) -> list[AmoCRMCatalogField]:
        """Returns chosen catalog's fields"""
        response = self.http.get(url=f"/api/v4/catalogs/{catalog_id}/custom_fields", params={"limit": 250})  # request max amount of fields for catalog
        return [AmoCRMCatalogField.from_json(catalog) for catalog in response["_embedded"]["custom_fields"]]

    def get_pipelines(self) -> list[AmoCRMPipeline]:
        """
        Returns all amocrm_lead pipelines from amocrm

        https://www.amocrm.ru/developers/content/crm_platform/leads_pipelines
        """
        response = self.http.get(url="/api/v4/leads/pipelines")
        return [AmoCRMPipeline.from_json(pipeline) for pipeline in response["_embedded"]["pipelines"]]
