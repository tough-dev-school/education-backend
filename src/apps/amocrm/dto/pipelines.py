from apps.amocrm import types
from apps.amocrm.client import http


class AmoCRMPipelinesDTO:  # NOQA: PIE798
    @classmethod
    def get(cls) -> list[types.Pipeline]:
        """
        Returns all amocrm pipelines
        https://www.amocrm.ru/developers/content/crm_platform/leads_pipelines
        """
        response = http.get(url="/api/v4/leads/pipelines", cached=True)
        return [cls._pipeline_from_response(data=pipeline) for pipeline in response["_embedded"]["pipelines"]]

    @staticmethod
    def _pipeline_from_response(data: dict) -> types.Pipeline:
        return types.Pipeline(
            id=data["id"],
            name=data["name"],
            statuses=[types.PipelineStatus(id=status["id"], name=status["name"]) for status in data["_embedded"]["statuses"]],
        )
