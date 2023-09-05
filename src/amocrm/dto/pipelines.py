from typing import TypedDict

from amocrm.dto.base import AmoDTO


class PipelineStatus(TypedDict):
    id: int
    name: str


class Pipeline(TypedDict):
    id: int
    name: str
    statuses: list[PipelineStatus]


class AmoCRMPipelines(AmoDTO):
    def get(self) -> list[Pipeline]:
        """
        Returns all amocrm pipelines
        https://www.amocrm.ru/developers/content/crm_platform/leads_pipelines
        """
        response = self.http.get(url="/api/v4/leads/pipelines")
        return [self._pipeline_from_response(data=pipeline) for pipeline in response["_embedded"]["pipelines"]]

    def _pipeline_from_response(self, data: dict) -> Pipeline:
        return Pipeline(
            id=data["id"],
            name=data["name"],
            statuses=[self._pipeline_status_from_response(data=status) for status in data["_embedded"]["statuses"]],
        )

    def _pipeline_status_from_response(self, data: dict) -> PipelineStatus:
        return PipelineStatus(
            id=data["id"],
            name=data["name"],
        )
