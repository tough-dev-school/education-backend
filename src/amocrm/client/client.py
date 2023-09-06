from amocrm.client.http import AmoCRMHTTP
from amocrm.types import AmoCRMCatalogField


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
