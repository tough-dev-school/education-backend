from typing import Literal

from django.core.cache import cache

from amocrm.client import AmoCRMClient
from amocrm.exceptions import AmoCRMCacheException

PIPELINE_NAMES = Literal["b2c", "b2b", "individual"]
PIPELINE_TO_CACHE = {
    "b2c": "amocrm_b2c_pipeline_id",
    "b2b": "amocrm_b2b_pipeline_id",
    "individual": "amocrm_individual_pipeline_id",
}


def get_pipeline_id_amocrm(pipeline_name: PIPELINE_NAMES) -> int:
    client = AmoCRMClient()
    pipelines = [pipeline for pipeline in client.get_pipelines() if pipeline.name == pipeline_name]
    if len(pipelines) != 1:
        raise AmoCRMCacheException(f"Cannot retrieve {pipeline_name} pipeline id")

    return pipelines[0].id


def get_pipeline_id(pipeline_name: PIPELINE_NAMES) -> int:
    cache_key = PIPELINE_TO_CACHE[pipeline_name]
    return cache.get_or_set(cache_key, lambda: get_pipeline_id_amocrm(pipeline_name), timeout=None)  # type: ignore


__all__ = ["get_pipeline_id"]
