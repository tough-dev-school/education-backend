import typing

from django.core.cache import cache

from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMCacheException

FIELDS_CODES = typing.Literal["POSITION", "PHONE", "EMAIL"]
FIELDS_TO_CACHE = {
    "POSITION": "amocrm_contacts_position_id",
    "PHONE": "amocrm_contacts_phone_id",
    "EMAIL": "amocrm_contacts_email_id",
}


def get_field_id_from_amocrm(field_code: FIELDS_CODES) -> int:
    client = AmoCRMClient()

    contact_fields = [field for field in client.get_contact_fields() if field.code == field_code]
    if len(contact_fields) != 1:
        raise AmoCRMCacheException(f"Cannot retrieve {field_code} contact field")

    return contact_fields[0].id


def get_contact_field_id(field_code: FIELDS_CODES) -> int:
    cache_key = FIELDS_TO_CACHE[field_code]
    return cache.get_or_set(cache_key, lambda: get_field_id_from_amocrm(field_code), timeout=None)  # type: ignore


__all__ = ["get_contact_field_id"]
