def normalize_single_value(value: dict | list | None = None) -> dict | list | None:
    """Returns Noner if value is not suitable"""
    if isinstance(value, dict):
        value = normalize_email_context(value)

    if isinstance(value, list):
        value = [normalize_single_value(i) for i in value]

    if value in [{}, []] or value is None:
        return None

    return value


def normalize_email_context(ctx: dict) -> dict:
    """Recursively strip values that are not suitable for mail providers"""

    normalized = {key: normalize_single_value(value) for key, value in ctx.items()}

    return {key: value for key, value in normalized.items() if value is not None}


__all__ = [
    "normalize_email_context",
]
