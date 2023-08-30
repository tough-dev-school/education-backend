from dataclasses import dataclass

from amocrm.entities.base import BaseAmoEntity
from users.models import User


@dataclass
class AmoCRMCustomer(BaseAmoEntity):
    user: User

    def create(self) -> int:
        """
        Creates customer and returns amocrm_id
        https://www.amocrm.ru/developers/content/crm_platform/customers-api#customers-add
        """
        response = self.http.post(
            url="/api/v4/customers",
            data=[self._user_as_customer_data],
        )

        return response["_embedded"]["customers"][0]["id"]

    def update(self, customer_id: int) -> None:
        """
        Updates existing in amocrm customer
        https://www.amocrm.ru/developers/content/crm_platform/customers-api#customers-edit
        """
        data = self._user_as_customer_data
        data.update({"id": customer_id})

        self.http.patch(
            url="/api/v4/customers",
            data=[data],
        )

    def link_to_contact(self, customer_id: int, contact_id: int) -> None:
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
