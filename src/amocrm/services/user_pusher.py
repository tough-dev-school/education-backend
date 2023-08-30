from dataclasses import dataclass

from amocrm.dto import AmoCRMCustomer
from amocrm.models import AmoCRMUser
from app.services import BaseService
from users.models import User


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
        customer_id, contact_id = AmoCRMCustomer(user=user).create()
        AmoCRMUser.objects.create(
            user=user,
            customer_id=customer_id,
            contact_id=contact_id,
        )

    def update_user(self, user: User) -> None:
        AmoCRMCustomer(user=user).update()
