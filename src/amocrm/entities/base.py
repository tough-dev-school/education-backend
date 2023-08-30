from dataclasses import dataclass

from amocrm.client.http import AmoCRMHTTP


@dataclass
class AmoDTO:
    def __post_init__(self) -> None:
        self.http = AmoCRMHTTP()
