from dataclasses import dataclass

from amocrm.cache.contact_fields_ids import get_contact_field_id
from amocrm.entities.base import AmoDTO
from users.models import User


@dataclass
class AmoCRMCustomer(AmoDTO):
    user: User

    def create_customer(self) -> int:
        """
        Creates customer and returns amocrm_id
        https://www.amocrm.ru/developers/content/crm_platform/customers-api#customers-add
        """
        response = self.http.post(
            url="/api/v4/customers",
            data=[self._user_as_customer],
        )

        return response["_embedded"]["customers"][0]["id"]

    def update_customer(self, customer_id: int) -> None:
        """
        Updates existing in amocrm customer
        https://www.amocrm.ru/developers/content/crm_platform/customers-api#customers-edit
        """
        data = self._user_as_customer
        data.update({"id": customer_id})

        self.http.patch(
            url="/api/v4/customers",
            data=[data],
        )

    def create_contact(self) -> int:
        """
        Creates contact and returns amocrm_id
        https://www.amocrm.ru/developers/content/crm_platform/contacts-api#contacts-add
        """
        response = self.http.post(
            url="/api/v4/contacts",
            data=[self._user_as_contact],
        )

        return response["_embedded"]["contacts"][0]["id"]

    def update_contact(self, contact_id: int) -> None:
        """
        Updates existing in amocrm contact
        https://www.amocrm.ru/developers/content/crm_platform/contacts-api#contacts-edit
        """
        data = self._user_as_contact
        data.update({"id": contact_id})

        self.http.patch(
            url="/api/v4/contacts",
            data=[data],
        )

    def link_customer_to_contact(self, customer_id: int, contact_id: int) -> None:
        """
        Link given customer to given contact
        https://www.amocrm.ru/developers/content/crm_platform/entity-links-api#links-link
        """
        self.http.post(
            url=f"/api/v4/customers/{customer_id}/link",
            data=[
                {
                    "to_entity_id": contact_id,
                    "to_entity_type": "contacts",
                },
            ],
        )

    @property
    def _user_as_customer(self) -> dict:
        return {
            "name": str(self.user),
            "_embedded": {
                "tags": [{"name": tag} for tag in self.user.tags],
            },
        }

    @property
    def _user_as_contact(self) -> dict:
        return {
            "name": str(self.user),
            "custom_fields_values": [
                {
                    "field_id": get_contact_field_id(field_code="EMAIL"),
                    "values": [
                        {"value": self.user.email},
                    ],
                },
            ],
        }
