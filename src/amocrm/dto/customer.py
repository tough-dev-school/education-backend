from dataclasses import dataclass

from amocrm.client import http
from users.models import User


@dataclass
class AmoCRMCustomer:
    user: User

    def create(self) -> tuple[int, int]:
        """
        Create related Customer and Contact
        returns customer_id and contact_id
        """
        customer_id = self._create_customer()
        contact_id = self._create_contact()
        self._link_customer_to_contact(customer_id=customer_id, contact_id=contact_id)
        return customer_id, contact_id

    def update(self) -> None:
        """Update customer and contact for given user"""
        self._update_customer(customer_id=self.user.amocrm_user.customer_id)
        self._update_contact(contact_id=self.user.amocrm_user.contact_id)

    def _create_customer(self) -> int:
        """
        Creates customer and returns amocrm_id
        https://www.amocrm.ru/developers/content/crm_platform/customers-api#customers-add
        """
        response = http.post(
            url="/api/v4/customers",
            data=[self._get_user_as_customer()],
        )

        return response["_embedded"]["customers"][0]["id"]

    def _update_customer(self, customer_id: int) -> None:
        """
        Updates existing in amocrm customer
        https://www.amocrm.ru/developers/content/crm_platform/customers-api#customers-edit
        """
        data = self._get_user_as_customer()
        data.update({"id": customer_id})

        http.patch(
            url="/api/v4/customers",
            data=[data],
        )

    def _create_contact(self) -> int:
        """
        Creates contact and returns amocrm_id
        https://www.amocrm.ru/developers/content/crm_platform/contacts-api#contacts-add
        """
        response = http.post(
            url="/api/v4/contacts",
            data=[self._get_user_as_contact()],
        )

        return response["_embedded"]["contacts"][0]["id"]

    def _update_contact(self, contact_id: int) -> None:
        """
        Updates existing in amocrm contact
        https://www.amocrm.ru/developers/content/crm_platform/contacts-api#contacts-edit
        """
        data = self._get_user_as_contact()
        data.update({"id": contact_id})

        http.patch(
            url="/api/v4/contacts",
            data=[data],
        )

    def _link_customer_to_contact(self, customer_id: int, contact_id: int) -> None:
        """
        Link given customer to given contact
        https://www.amocrm.ru/developers/content/crm_platform/entity-links-api#links-link
        """
        http.post(
            url=f"/api/v4/customers/{customer_id}/link",
            data=[
                {
                    "to_entity_id": contact_id,
                    "to_entity_type": "contacts",
                },
            ],
        )

    def _get_user_as_customer(self) -> dict:
        return {
            "name": str(self.user),
            "_embedded": {
                "tags": [{"name": tag} for tag in self.user.tags],
            },
        }

    def _get_user_as_contact(self) -> dict:
        from amocrm.ids import contact_field_id

        return {
            "name": str(self.user),
            "custom_fields_values": [
                {
                    "field_id": contact_field_id(field_code="EMAIL"),
                    "values": [
                        {"value": self.user.email},
                    ],
                },
            ],
        }
