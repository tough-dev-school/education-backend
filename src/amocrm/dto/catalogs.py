from typing import TypedDict

from amocrm.dto.base import AmoDTO


class CatalogField(TypedDict):
    id: int
    code: str


class Catalog(TypedDict):
    id: int
    name: str
    type: str


class AmoCRMCatalogs(AmoDTO):
    def get(self) -> list[Catalog]:
        """
        Returns all catalogs from amocrm
        https://www.amocrm.ru/developers/content/crm_platform/catalogs-api#lists-list
        """
        response = self.http.get(url="/api/v4/catalogs", params={"limit": 250})  # request max amount of catalogs
        return [self._catalog_from_response(catalog) for catalog in response["_embedded"]["catalogs"]]

    def get_fields(self, catalog_id: int) -> list[CatalogField]:
        """
        Returns chosen catalog's fields
        https://www.amocrm.ru/developers/content/crm_platform/custom-fields
        """
        response = self.http.get(url=f"/api/v4/catalogs/{catalog_id}/custom_fields", params={"limit": 250})  # request max amount of fields for catalog
        return [self._catalog_field_from_response(catalog) for catalog in response["_embedded"]["custom_fields"]]

    @staticmethod
    def _catalog_from_response(data: dict) -> Catalog:
        return Catalog(
            id=data["id"],
            name=data["name"],
            type=data["type"],
        )

    @staticmethod
    def _catalog_field_from_response(data: dict) -> CatalogField:
        return CatalogField(
            id=data["id"],
            code=data["code"],
        )
