from dataclasses import asdict
from dataclasses import dataclass


@dataclass(frozen=True)
class AmoCRMCatalog:
    id: int
    name: str
    type: str


@dataclass(frozen=True)
class AmoCRMCatalogFieldValue:
    value: str
    id: int | None = None

    def to_json(self) -> dict:
        return {key: value for key, value in asdict(self).items() if value is not None}


@dataclass(frozen=True)
class AmoCRMCatalogField:
    id: int
    name: str
    type: str
    code: str
    nested: list[AmoCRMCatalogFieldValue] | None = None

    @classmethod
    def from_json(cls, data: dict) -> "AmoCRMCatalogField":
        nested = data["nested"]
        if nested is not None:
            nested = [AmoCRMCatalogFieldValue(value=nested_data["value"], id=nested_data["id"]) for nested_data in nested]
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            code=data["code"],
            nested=nested,
        )
