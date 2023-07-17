from django.conf import settings

from app.integrations.dashamail.exceptions import DashamailSubscriptionFailed
from app.integrations.dashamail.exceptions import DashamailUpdateFailed
from app.integrations.dashamail.http import DashamailHTTP


class AppDashamail:
    def __init__(self) -> None:
        self.http = DashamailHTTP()
        self.list_id = settings.DASHAMAIL_LIST_ID

    def subscribe_user(self, email: str, first_name: str, last_name: str, tags: list[str]) -> None:
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
            raise DashamailSubscriptionFailed(f"{response}")

    def get_subscriber(self, email: str) -> tuple[int | None, bool]:
        """Return tuple which consists of member_id and is_active"""
        if email.endswith("@ya.ru"):
            # Dashamail internally convert ya.ru to yandex.ru, with ya.ru we're going to get nothing
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

    def update_subscriber(self, member_id: int, first_name: str, last_name: str, tags: list[str]) -> None:
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
            raise DashamailUpdateFailed(f"{response}")


__all__ = [
    "AppDashamail",
]
