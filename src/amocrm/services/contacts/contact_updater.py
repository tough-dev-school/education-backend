from dataclasses import dataclass

from amocrm.cache.contact_fields_ids import get_contact_field_id
from amocrm.client import AmoCRMClient
from amocrm.models import AmoCRMUserContact
from amocrm.types import AmoCRMCatalogElement
from amocrm.types import AmoCRMCatalogElementField
from amocrm.types import AmoCRMCatalogElementFieldValue
from app.services import BaseService


@dataclass
class AmoCRMContactUpdater(BaseService):
    """
    Updates Contact in AmoCRM for given user
    Returns id of updated AmoCRM entity
    """

    amocrm_user_contact: AmoCRMUserContact

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()
        self.user = self.amocrm_user_contact.user

    def act(self) -> int:
        user_as_contact_element = AmoCRMCatalogElement(
            id=self.amocrm_user_contact.amocrm_id,
            name=str(self.user),
            custom_fields_values=self.get_fields_values(),
        )

        return self.client.update_contact(
            user_as_contact_element=user_as_contact_element,
        )

    def get_fields_values(self) -> list[AmoCRMCatalogElementField]:
        fields_values = []
        if self.user.email and len(self.user.email):
            email_field = AmoCRMCatalogElementField(
                field_id=self.email_field_id,
                values=[AmoCRMCatalogElementFieldValue(value=self.user.email)],
            )
            fields_values.append(email_field)
        return fields_values

    @property
    def email_field_id(self) -> int:
        return get_contact_field_id(field_code="EMAIL")
