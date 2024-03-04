from dataclasses import dataclass
from typing import TYPE_CHECKING

from django.conf import settings

from apps.dashamail import exceptions
from apps.dashamail.lists.dto.base import DashamailListsDTO
from apps.dashamail.lists.dto.list import DashamailList

if TYPE_CHECKING:
    from apps.users.models import User


@dataclass
class DashamailSubscriber(DashamailListsDTO):
    user: "User"

    def subscribe(self, to: DashamailList | None = None) -> None:
        mail_list = to if to is not None else self.get_default_list()

        if self.get_member_id(mail_list) is None:
            self._subscribe(to=mail_list)
        else:
            self._update(mail_list)

    def _subscribe(self, to: DashamailList) -> None:
        response = self.api.call(
            "lists.add_member",
            {
                "list_id": str(to.list_id),
                "email": self.format_email(self.user.email),
                "merge_1": self.user.first_name,
                "merge_2": self.user.last_name,
                "merge_3": ";".join(self.user.tags),
            },
        )

        if response["response"]["msg"]["err_code"] != 0:
            raise exceptions.DashamailSubscriptionFailed(f"{response}")

    def _update(self, mail_list: DashamailList) -> None:
        """Replace old user's fields with new"""

        response = self.api.call(
            "lists.update_member",
            {
                "list_id": str(mail_list.list_id),
                "merge_1": self.user.first_name,
                "merge_2": self.user.last_name,
                "member_id": str(self.get_member_id(mail_list)),
                "merge_3": ";".join(self.user.tags),
            },
        )

        if response["response"]["msg"]["err_code"] != 0:
            raise exceptions.DashamailUpdateFailed(f"{response}")

    def get_member_id(self, mail_list: DashamailList) -> int | None:
        """Return tuple which consists of member_id and is_active"""
        response = self.api.call(
            "lists.get_members",
            {
                "list_id": str(mail_list.list_id),
                "email": self.format_email(self.user.email),
            },
        )

        if response["response"]["msg"]["err_code"] != 0:
            return None

        return int(response["response"]["data"][0]["id"])

    @staticmethod
    def get_default_list() -> DashamailList:
        return DashamailList(list_id=settings.DASHAMAIL_LIST_ID)

    @staticmethod
    def format_email(email: str) -> str:
        if email.endswith("@ya.ru"):
            # Dashamail internally converts ya.ru to yandex.ru, with ya.ru we're going to get nothing
            return email.replace("@ya.ru", "@yandex.ru")

        return email
