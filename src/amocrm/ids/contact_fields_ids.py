import typing

from amocrm.dto.catalogs import AmoCRMCatalogs
from amocrm.exceptions import AmoCRMCacheException

FIELDS_CODES = typing.Literal["POSITION", "PHONE", "EMAIL"]


def get_contact_field_id(field_code: FIELDS_CODES) -> int:
    contact_fields = [field for field in AmoCRMCatalogs.get_contacts_fields() if field["code"] == field_code]
    if len(contact_fields) != 1:
        raise AmoCRMCacheException(f"Cannot retrieve {field_code} contact field")

    return contact_fields[0]["id"]
