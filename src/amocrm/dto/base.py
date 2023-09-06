from dataclasses import dataclass

from amocrm.client.http import AmoCRMHTTP


@dataclass
class AmoDTO:
    @classmethod  # type: ignore
    @property
    def http(cls) -> AmoCRMHTTP:
        return AmoCRMHTTP()
