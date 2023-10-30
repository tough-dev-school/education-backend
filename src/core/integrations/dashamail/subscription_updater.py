from dataclasses import dataclass
from typing import final, TYPE_CHECKING

from core.integrations.dashamail import AppDashamail
from core.services import BaseService

if TYPE_CHECKING:
    from apps.users.models import User


@final
@dataclass
class SubscriptionUpdater(BaseService):
    """
    Update user in dashamail

    if user didn't exist there -> create new subscription
    if user exist, even inactive -> update user's info
    """

    user: "User"

    dashamail: AppDashamail = AppDashamail()

    def act(self) -> None:
        member_id, is_active = self.dashamail.get_subscriber(self.user.email)

        if member_id is None:
            self.dashamail.subscribe_user(
                email=self.user.email,
                first_name=self.user.first_name,
                last_name=self.user.last_name,
                tags=self.user.tags,
            )
        else:
            self.dashamail.update_subscriber(
                member_id=member_id,
                first_name=self.user.first_name,
                last_name=self.user.last_name,
                tags=self.user.tags,
            )
