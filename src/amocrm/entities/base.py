from dataclasses import dataclass

from amocrm.client.http import AmoCRMHTTP


@dataclass
class BaseAmoEntity:
    def __post_init__(self) -> None:
        self.http = AmoCRMHTTP()
