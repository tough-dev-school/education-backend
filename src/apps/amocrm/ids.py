from typing import Literal

from django.conf import settings

from apps.amocrm import types
from apps.amocrm.dto import AmoCRMCatalogsDTO
from apps.amocrm.dto import AmoCRMPipelinesDTO
from apps.amocrm.exceptions import AmoCRMCacheException

STATUSES_NAMES = Literal["unsorted", "first_contact", "purchased", "closed"]
STATUSES_NAMES_TRANSLATE = {
    "unsorted": "Неразобранное",
    "first_contact": "новое обращение",
    "purchased": "Успешно реализовано",
    "closed": "Закрыто и не реализовано",
}
PRODUCTS_FIELDS_CODES = Literal["SKU", "PRICE", "SPECIAL_PRICE_1", "GROUP", "DESCRIPTION", "EXTERNAL_ID", "UNIT"]
CONTACTS_FIELDS_CODES = Literal["POSITION", "PHONE", "EMAIL"]


def _b2c_pipeline() -> types.Pipeline:
    for pipeline in AmoCRMPipelinesDTO.get():
        if pipeline.name == settings.AMOCRM_B2C_PIPELINE_NAME:
            return pipeline
    raise AmoCRMCacheException("Cannot retrieve b2c pipeline")


def b2c_pipeline_status_id(status_name: STATUSES_NAMES) -> int:
    ru_status = STATUSES_NAMES_TRANSLATE[status_name]
    for status in _b2c_pipeline().statuses:
        if status.name == ru_status:
            return status.id

    raise AmoCRMCacheException(f"Cannot retrieve {status_name} ({ru_status}) status in {settings.AMOCRM_B2C_PIPELINE_NAME} pipeline")


def b2c_pipeline_id() -> int:
    return _b2c_pipeline().id


def contact_field_id(field_code: CONTACTS_FIELDS_CODES) -> int:
    for field in AmoCRMCatalogsDTO.get_contacts_fields():
        if field.code == field_code:
            return field.id
    raise AmoCRMCacheException(f"Cannot retrieve {field_code} contact field")


def products_catalog_id() -> int:
    for catalog in AmoCRMCatalogsDTO.get():
        if catalog.type == "products":
            return catalog.id
    raise AmoCRMCacheException("Cannot retrieve products catalog id")


def product_field_id(field_code: PRODUCTS_FIELDS_CODES) -> int:
    product_catalog_id = products_catalog_id()
    for field in AmoCRMCatalogsDTO.get_fields(catalog_id=product_catalog_id):
        if field.code == field_code:
            return field.id
    raise AmoCRMCacheException(f"Cannot retrieve {field_code} product field")


__all__ = [
    "b2c_pipeline_status_id",
    "b2c_pipeline_id",
    "contact_field_id",
    "products_catalog_id",
    "product_field_id",
]
