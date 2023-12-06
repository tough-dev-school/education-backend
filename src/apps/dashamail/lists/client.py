from django.conf import settings

from apps.dashamail import exceptions
from apps.dashamail.lists.http import DashamailListsHTTP
from apps.users.models import User


class DashamailListsClient:
    """Dealing with dashamail lists"""

    def __init__(self) -> None:
        self.http = DashamailListsHTTP()
        self.list_id = settings.DASHAMAIL_LIST_ID

    def subscribe_or_update(self, user: User) -> None:
        member_id, _ = self._get_member_id(user.email)

        if member_id is None:
            self._subscribe(
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                tags=user.tags,
            )
        else:
            self._update_subscriber(
                member_id=member_id,
                first_name=user.first_name,
                last_name=user.last_name,
                tags=user.tags,
            )

    def _subscribe(self, email: str, first_name: str, last_name: str, tags: list[str]) -> None:
        payload = {
            "method": "lists.add_member",
            "list_id": self.list_id,
            "email": email,
            "merge_1": first_name,
            "merge_2": last_name,
            "merge_3": ";".join(tags),
        }

        response = self.http.post(
            url="",
            payload=payload,
        )

        if response["response"]["msg"]["err_code"] != 0:
            raise exceptions.DashamailSubscriptionFailed(f"{response}")

    def _get_member_id(self, email: str) -> tuple[int | None, bool]:
        """Return tuple which consists of member_id and is_active"""
        if email.endswith("@ya.ru"):
            # Dashamail internally converts ya.ru to yandex.ru, with ya.ru we're going to get nothing
            email = email.replace("@ya.ru", "@yandex.ru")

        payload = {
            "method": "lists.get_members",
            "list_id": self.list_id,
            "email": email,
        }

        response = self.http.post(
            url="",
            payload=payload,
        )

        if response["response"]["msg"]["err_code"] != 0:
            return None, False

        return (
            int(response["response"]["data"][0]["id"]),
            response["response"]["data"][0]["state"] == "active",
        )

    def _update_subscriber(self, member_id: int, first_name: str, last_name: str, tags: list[str]) -> None:
        """Replace old user's fields with new"""

        payload = {
            "method": "lists.update_member",
            "list_id": self.list_id,
            "merge_1": first_name,
            "merge_2": last_name,
            "member_id": member_id,
            "merge_3": ";".join(tags),
        }

        response = self.http.post(
            url="",
            payload=payload,
        )

        if response["response"]["msg"]["err_code"] != 0:
            raise exceptions.DashamailUpdateFailed(f"{response}")


__all__ = [
    "DashamailListsClient",
]
