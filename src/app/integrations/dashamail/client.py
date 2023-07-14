from app.integrations.dashamail.exceptions import DashamailSubscriptionFailed
from app.integrations.dashamail.exceptions import DashamailUpdateFailed
from app.integrations.dashamail.http import DashamailHTTP


class AppDashamail:
    def __init__(self) -> None:
        self.http = DashamailHTTP()

    def subscribe_user(self, email: str, first_name: str, last_name: str, tags: list[str]) -> None:
        payload = {
            "method": "lists.add_member",
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

        payload = {
            "method": "lists.get_members",
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
