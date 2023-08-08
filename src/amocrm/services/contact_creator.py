from dataclasses import dataclass
from typing import Callable

from amocrm.cache.contact_fields_ids import get_contact_field_id
from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMServiceException
from amocrm.models import AmoCRMUserContact
from amocrm.types import AmoCRMCatalogElement
from amocrm.types import AmoCRMCatalogElementField
from amocrm.types import AmoCRMCatalogElementFieldValue
from app.services import BaseService
from users.models import User


class AmoCRMContactCreatorException(AmoCRMServiceException):
    """Raises when it's impossible to create amocrm contact"""


@dataclass
class AmoCRMContactCreator(BaseService):
    """
    Creates Contact in AmoCRM for given user
    Returns id of created AmoCRM entity
    """

    user: User

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()

    def act(self) -> int:
        user_as_contact_element = AmoCRMCatalogElement(
            name=str(self.user),
            custom_fields_values=self.get_fields_values(),
        )

        amocrm_contact_id = self.client.create_contact(
            user_as_contact_element=user_as_contact_element,
        )

        amocrm_course = AmoCRMUserContact.objects.create(user=self.user, amocrm_id=amocrm_contact_id)
        return amocrm_course.amocrm_id

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

    def get_validators(self) -> list[Callable]:
        return [self.validate_amocrm_contact_doesnt_exist]

    def validate_amocrm_contact_doesnt_exist(self) -> None:
        if hasattr(self.user, "amocrm_user_contact"):
            raise AmoCRMContactCreatorException("AmoCRMUserContact for this User already exists")
