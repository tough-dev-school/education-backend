from typing import Literal

from django.conf import settings
from django.core.cache import cache

from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMCacheException

STATUSES_NAMES = Literal["unsorted", "first_contact", "purchased", "closed"]
STATUSES_NAMES_TRANSLATE = {
    "unsorted": "Неразобранное",
    "first_contact": "новое обращение",
    "purchased": "Успешно реализовано",
    "closed": "Закрыто и не реализовано",
}
STATUSES_TO_CACHE = {
    "unsorted": "amocrm_b2c_unsorted_status_id",
    "first_contact": "amocrm_b2c_first_contact_status_id",
    "purchased": "amocrm_b2c_purchased_status_id",
    "closed": "amocrm_b2c_closed_status_id",
}
B2C_PIPELINE = settings.AMOCRM_B2C_PIPELINE_NAME


def get_pipeline_status_id_amocrm(status_name: STATUSES_NAMES) -> int:
    client = AmoCRMClient()

    pipelines = [pipeline for pipeline in client.get_pipelines() if pipeline.name == B2C_PIPELINE]
    if len(pipelines) != 1:
        raise AmoCRMCacheException(f"Cannot retrieve {B2C_PIPELINE} pipeline")

    ru_status = STATUSES_NAMES_TRANSLATE[status_name]
    for status in pipelines[0].statuses:
        if status.name == ru_status:
            return status.id

    raise AmoCRMCacheException(f"Cannot retrieve {status_name} ({ru_status}) status in {B2C_PIPELINE} pipeline")


def get_b2c_pipeline_status_id(status_name: STATUSES_NAMES) -> int:
    cache_key = STATUSES_TO_CACHE[status_name]
    return cache.get_or_set(cache_key, lambda: get_pipeline_status_id_amocrm(status_name), timeout=None)  # type: ignore


__all__ = ["get_b2c_pipeline_status_id"]
