from dataclasses import dataclass

from amocrm.cache.contact_fields_ids import get_contact_field_id
from amocrm.client import AmoCRMClient
from amocrm.models import AmoCRMUser
from amocrm.models import AmoCRMUserContact
from amocrm.types import AmoCRMCatalogElement
from amocrm.types import AmoCRMCatalogElementField
from amocrm.types import AmoCRMCatalogElementFieldValue
from amocrm.types import AmoCRMEntityLink
from app.services import BaseService
from orders.models import Order
from users.models import User


@dataclass
class AmoCRMUserPusher(BaseService):
    """
    Push given user to amocrm
    """

    user: User

    def __post_init__(self) -> None:
        self.client = AmoCRMClient()

    def act(self) -> None:
        if not self.user_must_be_pushed(user=self.user):
            return

        if hasattr(self.user, "amocrm_user") and hasattr(self.user, "amocrm_user_contact"):
            self.update_user(user=self.user)
        else:
            self.create_user(user=self.user)

    def create_user(self, user: User) -> None:
        customer_id = self.client.create_customer(user=user)
        contact_id = self.create_contact_id(user=user)
        self.link_contact_to_customer(customer_id=customer_id, contact_id=contact_id)

        AmoCRMUser.objects.create(user=user, amocrm_id=customer_id)
        AmoCRMUserContact.objects.create(user=user, amocrm_id=contact_id)

    def update_user(self, user: User) -> None:
        self.client.update_customer(amocrm_user=user.amocrm_user)
        self.update_contact(user=user)

    def create_contact_id(self, user: User) -> int:
        user_as_contact_element = AmoCRMCatalogElement(
            name=str(user),
            custom_fields_values=[self.get_email_field_value(user=user)],
        )

        return self.client.create_contact(user_as_contact_element=user_as_contact_element)

    def update_contact(self, user: User) -> None:
        user_as_contact_element = AmoCRMCatalogElement(
            id=user.amocrm_user_contact.amocrm_id,
            name=str(user),
            custom_fields_values=[self.get_email_field_value(user=user)],
        )

        self.client.update_contact(user_as_contact_element=user_as_contact_element)

    def link_contact_to_customer(self, customer_id: int, contact_id: int) -> None:
        contact_to_link = AmoCRMEntityLink(
            to_entity_id=contact_id,
            to_entity_type="contacts",
        )
        self.client.link_entity_to_another_entity(
            entity_type="customers",
            entity_id=customer_id,
            entity_to_link=contact_to_link,
        )

    @staticmethod
    def get_email_field_value(user: User) -> AmoCRMCatalogElementField:
        return AmoCRMCatalogElementField(
            field_id=get_contact_field_id(field_code="EMAIL"),
            values=[AmoCRMCatalogElementFieldValue(value=user.email)],
        )

    @staticmethod
    def user_must_be_pushed(user: User) -> bool:
        return Order.objects.filter(user=user).count() > 0  # type: ignore
