from dataclasses import dataclass
from typing import final, TYPE_CHECKING

from django.conf import settings

from app.integrations.dashamail import AppDashamail
from app.services import BaseService

if TYPE_CHECKING:
    from users.models import User


@final
@dataclass
class SubscriptionUpdater(BaseService):
    """
    Update user in dashamail

    if user didn't exist there -> create new subscription
    if user exist, even inactive -> update user's info
    """

    user: "User"
    list_id: str | None = None

    def __post_init__(self) -> None:
        self.dashamail = AppDashamail()

        if not self.list_id:
            self.list_id = settings.DASHAMAIL_LIST_ID

    def act(self) -> None:
        if not self.list_id:
            return

        member_id, is_active = self.dashamail.get_subscriber(list_id=self.list_id, email=self.user.email)

        if member_id is None:
            self.dashamail.subscribe_user(
                list_id=self.list_id,
                email=self.user.email,
                first_name=self.user.first_name,
                last_name=self.user.last_name,
                tags=self.user.tags,
            )
        else:
            self.dashamail.update_subscriber(
                list_id=self.list_id,
                member_id=member_id,
                first_name=self.user.first_name,
                last_name=self.user.last_name,
                tags=self.user.tags,
            )
