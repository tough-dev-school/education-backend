from dataclasses import dataclass

from apps.amocrm.dto import AmoCRMCustomerDTO
from apps.amocrm.models import AmoCRMUser
from apps.users.models import User
from core.services import BaseService


@dataclass
class AmoCRMUserPusher(BaseService):
    """Push given user to amocrm"""

    user: User

    def act(self) -> None:
        if not hasattr(self.user, "amocrm_user"):
            self.create_user(user=self.user)
        else:
            self.update_user(user=self.user)

    def create_user(self, user: User) -> None:
        customer_id, contact_id = AmoCRMCustomerDTO(user=user).create()
        AmoCRMUser.objects.create(
            user=user,
            customer_id=customer_id,
            contact_id=contact_id,
        )

    def update_user(self, user: User) -> None:
        AmoCRMCustomerDTO(user=user).update()
