from dataclasses import dataclass
from typing import Callable

from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMServiceException
from amocrm.types import AmoCRMEntityLink
from app.services import BaseService
from users.models import User


class AmoCRMContactToCustomerLinkerException(AmoCRMServiceException):
    """Raises when it's impossible to create link between contact and customer"""


@dataclass
class AmoCRMContactToCustomerLinker(BaseService):
    """
    Setup link between Contact and Customer for given user in AmoCRM
    """

    user: User

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()

    def act(self) -> None:
        contact_to_link = AmoCRMEntityLink(
            to_entity_id=self.user.amocrm_user_contact.amocrm_id,
            to_entity_type="contacts",
        )
        self.client.link_entity_to_another_entity(
            entity_type="customers",
            entity_id=self.user.amocrm_user.amocrm_id,
            entity_to_link=contact_to_link,
        )

    def get_validators(self) -> list[Callable]:
        return [
            self.validate_amocrm_contact_exist,
            self.validate_amocrm_customer_exist,
        ]

    def validate_amocrm_contact_exist(self) -> None:
        if not hasattr(self.user, "amocrm_user_contact"):
            raise AmoCRMContactToCustomerLinkerException("AmoCRMUserContact for this User doesn't exists")

    def validate_amocrm_customer_exist(self) -> None:
        if not hasattr(self.user, "amocrm_user"):
            raise AmoCRMContactToCustomerLinkerException("AmoCRMUser for this User doesn't exists")
