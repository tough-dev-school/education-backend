"""Fix fields that should be required in the schema, but for some reason drf-spectacular says they are not"""

from typing import Any

REQUIRED_FIELDS = [
    "modified",
    "created",
    "slug",
    "id",
    "uuid",
]


def process(result: dict, **kwargs: Any) -> dict:  # NOQA: ARG001
    schemas = result.get("components", {}).get("schemas", {})

    for schema in schemas.items():
        properties: list[str] = schema[1].get("properties", {}).keys()

        required: list[str] = schema[1].get("required", [])

        for field in REQUIRED_FIELDS:
            if field in properties and field not in required:
                required.append(field)

        schema[1]["required"] = required

    result["components"]["schemas"] = schemas

    return result
