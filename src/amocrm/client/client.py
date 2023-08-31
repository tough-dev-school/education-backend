from amocrm.client.http import AmoCRMHTTP
from amocrm.types import AmoCRMCatalog
from amocrm.types import AmoCRMCatalogElement
from amocrm.types import AmoCRMCatalogField
from amocrm.types import AmoCRMCatalogFieldValue
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

    def update_catalog_field(self, catalog_id: int, field_id: int, field_values: list[AmoCRMCatalogFieldValue]) -> list[AmoCRMCatalogFieldValue]:
        """
        Updates catalog field, must be used to create/update selectable field options
        returns list of AmoCRMCatalogFieldValue, every value has id from amocrm
        """
        response = self.http.patch(
            url=f"/api/v4/catalogs/{catalog_id}/custom_fields",
            data=[
                {"id": field_id, "nested": [field_value.to_json() for field_value in field_values]},
            ],
        )
        updated_field = response["_embedded"]["custom_fields"][0]
        return [AmoCRMCatalogFieldValue.from_json(updated_value) for updated_value in updated_field["nested"]]

    def create_catalog_element(self, catalog_id: int, element: AmoCRMCatalogElement) -> AmoCRMCatalogElement:
        """Creates catalog element in amocrm and returns it with amocrm_id"""
        response = self.http.post(
            url=f"/api/v4/catalogs/{catalog_id}/elements",
            data=[element.to_json()],
        )
        return AmoCRMCatalogElement.from_json(response["_embedded"]["elements"][0])

    def update_catalog_element(self, catalog_id: int, element: AmoCRMCatalogElement) -> AmoCRMCatalogElement:
        """Updates catalog element in amocrm and returns it with amocrm_id"""
        response = self.http.patch(
            url=f"/api/v4/catalogs/{catalog_id}/elements",
            data=[element.to_json()],
        )
        return AmoCRMCatalogElement.from_json(response["_embedded"]["elements"][0])

    def get_pipelines(self) -> list[AmoCRMPipeline]:
        """
        Returns all amocrm_lead pipelines from amocrm

        https://www.amocrm.ru/developers/content/crm_platform/leads_pipelines
        """
        response = self.http.get(url="/api/v4/leads/pipelines")
        return [AmoCRMPipeline.from_json(pipeline) for pipeline in response["_embedded"]["pipelines"]]
