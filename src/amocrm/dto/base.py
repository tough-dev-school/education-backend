from dataclasses import dataclass

from amocrm.client.http import AmoCRMHTTP


@dataclass
class AmoDTO:
    def __post_init__(self) -> None:
        self.http = self._get_http_client()

    @staticmethod
    def _get_http_client() -> AmoCRMHTTP:
        return AmoCRMHTTP()
