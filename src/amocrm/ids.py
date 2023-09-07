import typing
from typing import Literal

from django.conf import settings

from amocrm.dto import AmoCRMCatalogs
from amocrm.dto import AmoCRMPipelines
from amocrm.dto.pipelines import Pipeline
from amocrm.exceptions import AmoCRMCacheException

B2C_PIPELINE = settings.AMOCRM_B2C_PIPELINE_NAME
STATUSES_NAMES = Literal["unsorted", "first_contact", "purchased", "closed"]
STATUSES_NAMES_TRANSLATE = {
    "unsorted": "Неразобранное",
    "first_contact": "новое обращение",
    "purchased": "Успешно реализовано",
    "closed": "Закрыто и не реализовано",
}
PRODUCTS_FIELDS_CODES = Literal["SKU", "PRICE", "SPECIAL_PRICE_1", "GROUP", "DESCRIPTION", "EXTERNAL_ID", "UNIT"]
CONTACTS_FIELDS_CODES = Literal["POSITION", "PHONE", "EMAIL"]


def _get_b2c_pipeline() -> Pipeline:
    for pipeline in AmoCRMPipelines.get():
        if pipeline["name"] == B2C_PIPELINE:
            return pipeline
    raise AmoCRMCacheException("Cannot retrieve b2c pipeline")


def get_b2c_pipeline_status_id(status_name: STATUSES_NAMES) -> int:
    ru_status = STATUSES_NAMES_TRANSLATE[status_name]
    for status in _get_b2c_pipeline()["statuses"]:
        if status["name"] == ru_status:
            return status["id"]

    raise AmoCRMCacheException(f"Cannot retrieve {status_name} ({ru_status}) status in {B2C_PIPELINE} pipeline")


def get_b2c_pipeline_id() -> int:
    return _get_b2c_pipeline()["id"]


def get_contact_field_id(field_code: CONTACTS_FIELDS_CODES) -> int:
    for field in AmoCRMCatalogs.get_contacts_fields():
        if field["code"] == field_code:
            return field["id"]
    raise AmoCRMCacheException(f"Cannot retrieve {field_code} contact field")


def get_products_catalog_id() -> int:
    for catalog in AmoCRMCatalogs.get():
        if catalog["type"] == "products":
            return catalog["id"]
    raise AmoCRMCacheException("Cannot retrieve products catalog id")


def get_product_field_id(field_code: PRODUCTS_FIELDS_CODES) -> int:
    product_catalog_id = get_products_catalog_id()
    for field in AmoCRMCatalogs.get_fields(catalog_id=product_catalog_id):
        if field["code"] == field_code:
            return field["id"]
    raise AmoCRMCacheException(f"Cannot retrieve {field_code} product field")


__all__ = [
    "get_b2c_pipeline_status_id",
    "get_b2c_pipeline_id",
    "get_contact_field_id",
    "get_products_catalog_id",
    "get_product_field_id",
]
