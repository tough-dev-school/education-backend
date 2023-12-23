from apps.amocrm import types
from apps.amocrm.client import http


class AmoCRMCatalogsDTO:  # NOQA: PIE798
    @staticmethod
    def get() -> list[types.Catalog]:
        """
        Returns all catalogs from apps.amocrm
        https://www.amocrm.ru/developers/content/crm_platform/catalogs-api#lists-list
        """
        response = http.get(url="/api/v4/catalogs", params={"limit": 250}, cached=True)
        return [
            types.Catalog(
                id=catalog["id"],
                name=catalog["name"],
                type=catalog["type"],
            )
            for catalog in response["_embedded"]["catalogs"]
        ]

    @staticmethod
    def get_fields(catalog_id: int) -> list[types.CatalogField]:
        """
        Returns chosen catalog's fields
        https://www.amocrm.ru/developers/content/crm_platform/custom-fields
        """
        response = http.get(url=f"/api/v4/catalogs/{catalog_id}/custom_fields", params={"limit": 250}, cached=True)
        return [
            types.CatalogField(
                id=catalog["id"],
                code=catalog["code"],
            )
            for catalog in response["_embedded"]["custom_fields"]
        ]

    @staticmethod
    def get_contacts_fields() -> list[types.CatalogField]:
        """
        Returns contacts catalog fields
        https://www.amocrm.ru/developers/content/crm_platform/custom-fields
        """
        response = http.get(url="/api/v4/contacts/custom_fields", params={"limit": 250}, cached=True)
        return [
            types.CatalogField(
                id=contact["id"],
                code=contact["code"],
            )
            for contact in response["_embedded"]["custom_fields"]
        ]
