from dataclasses import asdict
from dataclasses import dataclass

from _decimal import Decimal


@dataclass(frozen=True)
class AmoCRMCatalogFieldValue:
    value: str | int | Decimal
    id: int | None = None

    def to_json(self) -> dict:
        return {key: value for key, value in asdict(self).items() if value is not None}

    @classmethod
    def from_json(cls, data: dict) -> "AmoCRMCatalogFieldValue":
        return cls(id=data["id"], value=data["value"])


@dataclass(frozen=True)
class AmoCRMCatalogField:
    id: int
    name: str
    type: str
    code: str
    nested: list[AmoCRMCatalogFieldValue] | None = None

    @classmethod
    def from_json(cls, data: dict) -> "AmoCRMCatalogField":
        nested = data.get("nested")
        if nested is not None:
            nested = [AmoCRMCatalogFieldValue.from_json(nested_data) for nested_data in nested]
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            code=data["code"],
            nested=nested,
        )
