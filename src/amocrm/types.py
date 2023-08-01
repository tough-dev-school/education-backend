from dataclasses import dataclass


@dataclass(frozen=True)
class AmoCRMCatalogField:
    id: int
    name: str
    type: str
