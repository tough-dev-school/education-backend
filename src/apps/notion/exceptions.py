class NotionError(Exception):
    ...


class NotSharedForWeb(NotionError):
    """Page has no results, may be you forgot to share it on the web?"""


class NotionResponseError(NotionError):
    """Notion returned some error"""


class HTTPError(NotionError):
    ...


__all__ = [
    "HTTPError",
    "NotionError",
    "NotSharedForWeb",
]
