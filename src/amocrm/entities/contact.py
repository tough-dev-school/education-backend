from dataclasses import dataclass

from amocrm.cache.contact_fields_ids import get_contact_field_id
from amocrm.entities.base import BaseAmoEntity
from users.models import User


@dataclass
class AmoCRMContact(BaseAmoEntity):
    user: User

    def create(self) -> int:
        """
        Creates contact and returns amocrm_id
        https://www.amocrm.ru/developers/content/crm_platform/contacts-api#contacts-add
        """
        response = self.http.post(
            url="/api/v4/contacts",
            data=[self._user_as_contact_data],
        )

        return response["_embedded"]["contacts"][0]["id"]

    def update(self, contact_id: int) -> None:
        """
        Updates existing in amocrm contact
        https://www.amocrm.ru/developers/content/crm_platform/contacts-api#contacts-edit
        """
        data = self._user_as_contact_data
        data.update({"id": contact_id})

        self.http.patch(
            url="/api/v4/contacts",
            data=[data],
        )

    @property
    def _user_as_contact_data(self) -> dict:
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
