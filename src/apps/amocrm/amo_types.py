from typing import NamedTuple


class CatalogField(NamedTuple):
    """Represents amocrm's custom catalog field that could be used with various entities
    https://www.amocrm.ru/developers/content/crm_platform/custom-fields
    """

    id: int
    code: str


class Catalog(NamedTuple):
    """Represents amocrm's catalog aka 'список'
    https://www.amocrm.ru/developers/content/crm_platform/catalogs-api#lists-list
    """

    id: int
    name: str
    type: str
