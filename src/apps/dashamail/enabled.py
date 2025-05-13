from django.conf import settings


def dashamail_enabled() -> bool:
    return settings.DASHAMAIL_API_KEY != ""


__all__ = ["dashamail_enabled"]
