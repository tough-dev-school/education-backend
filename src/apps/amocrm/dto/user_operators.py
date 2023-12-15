from typing import TypedDict

from apps.amocrm.client import http


class AmoCRMOperator(TypedDict):
    """Represents AmoCRM User. The 'Operator' is used to distinguish from the 'AmoCRMUser' model.

    Only fields that are used in the app are listed.
    All the available fields are listed in docs:
    https://www.amocrm.ru/developers/content/crm_platform/users-api#users-list
    """

    id: int
    name: str
    email: str


class AmoCRMOperatorDTO:
    """Methods to work with AmoCRM users."""

    def get_users(self) -> list[AmoCRMOperator]:
        """Return all the users from AmoCRM. The number of users is expected not to exceed 250, and pagination is not needed."""
        params = {"limit": 250}

        response_data = http.get(url="/api/v4/users", params=params, cached=True)

        return [
            AmoCRMOperator(
                id=user_data["id"],
                name=user_data["name"],
                email=user_data["email"],
            )
            for user_data in response_data["_embedded"]["users"]
        ]
