from amocrm.client.http import AmoCRMHTTP
from amocrm.models import AmoCRMUser
from users.models import User


class AmoCRMClient:
    """
    Client to deal with amoCRM with auto tokens refresh.
    """

    def __init__(self) -> None:
        self.http: AmoCRMHTTP = AmoCRMHTTP()

    def create_customer(self, user: User) -> int:
        """Creates customer and returns amocrm_id"""
        response = self.http.post(
            url="/api/v4/customers",
            data={"name": str(user), "_embedded": {"tags": [{"name": tag} for tag in user.tags]}},
        )

        return response["_embedded"]["customers"][0]["id"]

    def update_customer(self, amocrm_user: AmoCRMUser) -> int:
        """Updates existing in amocrm customer and returns amocrm_id"""
        response = self.http.patch(
            url="/api/v4/customers",
            data={"id": amocrm_user.amocrm_id, "name": str(amocrm_user.user), "_embedded": {"tags": [{"name": tag} for tag in amocrm_user.user.tags]}},
        )

        return response["_embedded"]["customers"][0]["id"]

    def enable_customers(self) -> None:
        """Enable customers list is required to create/update customers"""
        self.http.patch(url="/api/v4/customers/mode", data={"mode": "segments", "is_enabled": True})
