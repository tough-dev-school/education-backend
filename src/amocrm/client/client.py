from datetime import datetime

from _decimal import Decimal

from amocrm.client.http import AmoCRMHTTP
from amocrm.models import AmoCRMUser
from amocrm.types import AmoCRMCatalog
from amocrm.types import AmoCRMCatalogElement
from amocrm.types import AmoCRMCatalogField
from amocrm.types import AmoCRMCatalogFieldValue
from amocrm.types import AmoCRMEntityLink
from amocrm.types import AmoCRMPipeline
from amocrm.types import AmoCRMTransactionElement
from amocrm.types import ENTITY_TYPES
from users.models import User


class AmoCRMClient:
    """
    Client to deal with amoCRM with auto tokens refresh.
    """

    def __init__(self) -> None:
        self.http: AmoCRMHTTP = AmoCRMHTTP()

    def create_customer(self, user: User) -> int:
        """Creates customer and returns amocrm_id"""
        response = self.http.post(
            url="/api/v4/customers",
            data=[{"name": str(user), "_embedded": {"tags": [{"name": tag} for tag in user.tags]}}],
        )

        return response["_embedded"]["customers"][0]["id"]

    def update_customer(self, amocrm_user: AmoCRMUser) -> int:
        """Updates existing in amocrm customer and returns amocrm_id"""
        response = self.http.patch(
            url="/api/v4/customers",
            data=[{"id": amocrm_user.amocrm_id, "name": str(amocrm_user.user), "_embedded": {"tags": [{"name": tag} for tag in amocrm_user.user.tags]}}],
        )

        return response["_embedded"]["customers"][0]["id"]

    def create_contact(self, user_as_contact_element: AmoCRMCatalogElement) -> int:
        """Creates contact and returns amocrm_id"""
        response = self.http.post(
            url="/api/v4/contacts",
            data=[user_as_contact_element.to_json()],
        )

        return response["_embedded"]["contacts"][0]["id"]

    def update_contact(self, user_as_contact_element: AmoCRMCatalogElement) -> int:
        """Updates existing in amocrm contact and returns amocrm_id"""
        response = self.http.patch(
            url="/api/v4/contacts",
            data=[user_as_contact_element.to_json()],
        )

        return response["_embedded"]["contacts"][0]["id"]

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

    def link_entity_to_another_entity(self, entity_type: ENTITY_TYPES, entity_id: int, entity_to_link: AmoCRMEntityLink) -> None:
        """
        Setup link in AmoCRM between two different type entities

        contact to customer | product to amocrm_lead | contact to amocrm_lead | etc
        """
        self.http.post(url=f"/api/v4/{entity_type}/{entity_id}/link", data=[entity_to_link.to_json()])

    def create_lead(self, status_id: int, pipeline_id: int, contact_id: int, price: int | float | Decimal, created_at: datetime) -> int:
        """
        Creates amocrm_lead with contact in amocrm and returns its amocrm_id

        https://www.amocrm.ru/developers/content/crm_platform/leads-api#leads-complex-add
        """
        response = self.http.post(
            url="/api/v4/leads/complex",
            data=[
                {
                    "status_id": status_id,
                    "pipeline_id": pipeline_id,
                    "price": int(price),  # amocrm api requirement to send only integer
                    "created_at": int(created_at.timestamp()),  # amocrm api requirement to send only integer timestamp
                    "_embedded": {"contacts": [{"id": contact_id}]},
                }
            ],
        )

        return response[0]["id"]  # type: ignore

    def update_lead(self, lead_id: int, status_id: int, price: int | float | Decimal, created_at: datetime) -> int:
        """
        Updates amocrm_lead in amocrm and returns its amocrm_id

        https://www.amocrm.ru/developers/content/crm_platform/leads-api#leads-edit
        """
        response = self.http.patch(
            url="/api/v4/leads",
            data=[
                {
                    "id": lead_id,
                    "status_id": status_id,
                    "price": int(price),  # amocrm api requirement to send only integer
                    "created_at": int(created_at.timestamp()),  # amocrm api requirement to send only integer timestamp
                }
            ],
        )

        return response["_embedded"]["leads"][0]["id"]

    def create_customer_transaction(self, customer_id: int, price: int | float | Decimal, order_slug: str, purchased_product: AmoCRMTransactionElement) -> int:
        """
        Creates transaction for customer and returns its amocrm_id

        https://www.amocrm.ru/developers/content/crm_platform/customers-api#transactions-add
        """
        response = self.http.post(
            url=f"/api/v4/customers/{customer_id}/transactions",
            data=[
                {
                    "comment": f"Order slug in lms: {order_slug}",
                    "price": int(price),  # amocrm api requirement to send only integer
                    "_embedded": {"catalog_elements": [purchased_product.to_json()]},
                }
            ],
        )

        return response["_embedded"]["transactions"][0]["id"]

    def delete_transaction(self, transaction_id: int) -> None:
        """
        Deletes transaction for customer

        https://www.amocrm.ru/developers/content/crm_platform/customers-api#transactions-delete
        """
        self.http.delete(
            url=f"/api/v4/customers/transactions/{transaction_id}",
            expected_status_codes=[204],
        )

    def get_pipelines(self) -> list[AmoCRMPipeline]:
        """
        Returns all amocrm_lead pipelines from amocrm

        https://www.amocrm.ru/developers/content/crm_platform/leads_pipelines
        """
        response = self.http.get(url="/api/v4/leads/pipelines")
        return [AmoCRMPipeline.from_json(pipeline) for pipeline in response["_embedded"]["pipelines"]]
