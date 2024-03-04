from apps.amocrm import types
from apps.amocrm.client import http


class AmoCRMUserOperatorDTO:
    """Methods to work with AmoCRM users.

    The name as 'UserOperator' is chosen to distinguish from 'AmoCRMUser' model that link amocrm's customers.
    """

    def get(self) -> list[types.UserOperator]:
        """Return all the users from AmoCRM. The number of users is expected not to exceed 250, and pagination is not needed."""
        params = {"limit": 250}

        response_data = http.get(url="/api/v4/users", params=params, cached=True)

        return [
            types.UserOperator(
                id=user_data["id"],
                name=user_data["name"],
                email=user_data["email"],
            )
            for user_data in response_data["_embedded"]["users"]
        ]
