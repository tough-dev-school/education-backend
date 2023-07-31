from functools import wraps
from typing import Any, Callable

from django.conf import settings
from django.core.cache import cache

from amocrm.client.http import AmoCRMHTTP
from amocrm.models import AmoCRMUser
from amocrm.types import AmoCRMCatalog
from amocrm.types import AmoCRMCatalogField
from users.models import User


def auto_refresh_token(function: Callable) -> Any:
    @wraps(function)
    def wrapper(client: "AmoCRMClient", *args: Any, **kwargs: Any) -> Any:
        if cache.get("amocrm_access_token") is None:
            client.refresh_tokens()
        return function(client, *args, **kwargs)

    return wrapper


class AmoCRMClient:
    """
    Client to deal with amoCRM with auto tokens refresh.
    """

    def __init__(self) -> None:
        self.http: AmoCRMHTTP = AmoCRMHTTP()

    @auto_refresh_token
    def create_customer(self, user: User) -> int:
        """Creates customer and returns amocrm_id"""
        response = self.http.post(
            url="/api/v4/customers",
            data={"name": str(user), "_embedded": {"tags": [{"name": tag} for tag in user.tags]}},
        )

        return response["_embedded"]["customers"][0]["id"]

    @auto_refresh_token
    def update_customer(self, amocrm_user: AmoCRMUser) -> int:
        """Updates existing in amocrm customer and returns amocrm_id"""
        response = self.http.post(
            url="/api/v4/customers",
            data={"id": amocrm_user.amocrm_id, "name": str(amocrm_user.user), "_embedded": {"tags": [{"name": tag} for tag in amocrm_user.user.tags]}},
        )

        return response["_embedded"]["customers"][0]["id"]

    @auto_refresh_token
    def enable_customers(self) -> None:
        """Enable customers list is required to create/update customers"""
        self.http.patch(url="/api/v4/customers/mode", data={"mode": "segments", "is_enabled": True})

    def refresh_tokens(self) -> None:
        """Refresh auth tokens"""
        response = self.http.post(
            url="/oauth2/access_token",
            data={
                "client_id": settings.AMOCRM_INTEGRATION_ID,
                "client_secret": settings.AMOCRM_CLIENT_SECRET,
                "grant_type": "refresh_token",
                "code": cache.get("amocrm_refresh_token"),
                "redirect_uri": settings.AMOCRM_REDIRECT_URL,
            },
        )

        timeout = int(got["expires_in"]) - 60 * 5  # refresh tokens 5 min before expiration time
        cache.set("amocrm_access_token", got["access_token"], timeout=timeout)
        cache.set("amocrm_refresh_token", got["refresh_token"])

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

    def get_catalogs(self) -> list[AmoCRMCatalog]:
        """Returns all catalogs from amocrm"""
        response = self.http.get(url="/api/v2/catalogs", params={"limit": 250})  # request max amount of catalogs
        return [AmoCRMCatalog(id=catalog["id"], name=catalog["name"], type=catalog["type"]) for catalog in response["_embedded"]["items"]]

    def get_catalog_fields(self, catalog_id: int) -> list[AmoCRMCatalogField]:
        """Returns chosen catalog's fields"""
        response = self.http.get(url=f"/api/v2/catalogs/{catalog_id}/custom_fields", params={"limit": 250})  # request max amount of fields for catalog
        return [AmoCRMCatalogField.from_json(catalog) for catalog in response["_embedded"]["custom_fields"]]
