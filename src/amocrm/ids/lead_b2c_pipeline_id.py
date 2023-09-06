from typing import Literal

from django.conf import settings

from amocrm.dto.pipelines import AmoCRMPipelines
from amocrm.exceptions import AmoCRMCacheException

STATUSES_NAMES = Literal["unsorted", "first_contact", "purchased", "closed"]
STATUSES_NAMES_TRANSLATE = {
    "unsorted": "Неразобранное",
    "first_contact": "новое обращение",
    "purchased": "Успешно реализовано",
    "closed": "Закрыто и не реализовано",
}
B2C_PIPELINE = settings.AMOCRM_B2C_PIPELINE_NAME


def get_b2c_pipeline_status_id(status_name: STATUSES_NAMES) -> int:
    pipelines = [pipeline for pipeline in AmoCRMPipelines.get() if pipeline["name"] == B2C_PIPELINE]
    if len(pipelines) != 1:
        raise AmoCRMCacheException(f"Cannot retrieve {B2C_PIPELINE} pipeline")

    ru_status = STATUSES_NAMES_TRANSLATE[status_name]
    for status in pipelines[0]["statuses"]:
        if status["name"] == ru_status:
            return status["id"]

    raise AmoCRMCacheException(f"Cannot retrieve {status_name} ({ru_status}) status in {B2C_PIPELINE} pipeline")


def get_b2c_pipeline_id() -> int:
    pipelines = [pipeline for pipeline in AmoCRMPipelines.get() if pipeline["name"] == B2C_PIPELINE]
    if len(pipelines) != 1:
        raise AmoCRMCacheException("Cannot retrieve b2c pipeline id")

    return pipelines[0]["id"]
