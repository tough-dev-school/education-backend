from typing import TypedDict

from apps.amocrm.client import http


class PipelineStatus(TypedDict):
    id: int
    name: str


class Pipeline(TypedDict):
    id: int
    name: str
    statuses: list[PipelineStatus]


class AmoCRMPipelines:  # NOQA: PIE798
    @classmethod
    def get(cls) -> list[Pipeline]:
        """
        Returns all amocrm pipelines
        https://www.amocrm.ru/developers/content/crm_platform/leads_pipelines
        """
        response = http.get(url="/api/v4/leads/pipelines", cached=True)
        return [cls._pipeline_from_response(data=pipeline) for pipeline in response["_embedded"]["pipelines"]]

    @staticmethod
    def _pipeline_from_response(data: dict) -> Pipeline:
        return Pipeline(
            id=data["id"],
            name=data["name"],
            statuses=[PipelineStatus(id=status["id"], name=status["name"]) for status in data["_embedded"]["statuses"]],
        )
