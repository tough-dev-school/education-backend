from django.conf import settings
from django.core.cache import cache

from amocrm.dto.pipelines import AmoCRMPipelines
from amocrm.exceptions import AmoCRMCacheException


def get_pipeline_id_amocrm() -> int:
    pipelines = [pipeline for pipeline in AmoCRMPipelines().get() if pipeline["name"] == settings.AMOCRM_B2C_PIPELINE_NAME]
    if len(pipelines) != 1:
        raise AmoCRMCacheException("Cannot retrieve b2c pipeline id")

    return pipelines[0]["id"]


def get_b2c_pipeline_id() -> int:
    return cache.get_or_set("amocrm_b2c_pipeline_id", lambda: get_pipeline_id_amocrm(), timeout=None)  # type: ignore


__all__ = ["get_b2c_pipeline_id"]
