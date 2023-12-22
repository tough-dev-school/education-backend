from apps.amocrm import amo_types
from apps.amocrm.client import http


class AmoCRMPipelinesDTO:  # NOQA: PIE798
    @classmethod
    def get(cls) -> list[amo_types.Pipeline]:
        """
        Returns all amocrm pipelines
        https://www.amocrm.ru/developers/content/crm_platform/leads_pipelines
        """
        response = http.get(url="/api/v4/leads/pipelines", cached=True)
        return [cls._pipeline_from_response(data=pipeline) for pipeline in response["_embedded"]["pipelines"]]

    @staticmethod
    def _pipeline_from_response(data: dict) -> amo_types.Pipeline:
        return amo_types.Pipeline(
            id=data["id"],
            name=data["name"],
            statuses=[amo_types.PipelineStatus(id=status["id"], name=status["name"]) for status in data["_embedded"]["statuses"]],
        )
