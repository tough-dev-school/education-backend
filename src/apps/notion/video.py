from urllib.parse import parse_qs, urlparse


def get_youtube_video_id(url: str) -> str | None:
    parsed = urlparse(url)

    if parsed.netloc not in ["youtu.be", "www.youtube.com"]:
        return None

    if parsed.query is not None:
        query_string = parse_qs(parsed.query)
        if "v" in query_string:
            return query_string["v"][0]

    return parsed.path.replace("/", "")


def get_rutube_video_id(url: str) -> str | None:
    parsed = urlparse(url)

    if "rutube" not in parsed.netloc:
        return None

    return parsed.path.split("/")[-2]


def get_rutube_access_key(url: str) -> str | None:
    parsed = urlparse(url)

    if "rutube" not in parsed.netloc or not parsed.query:
        return None

    query_string = parse_qs(parsed.query)
    if "p" in query_string:
        return query_string["p"][0]

    return None


__all__ = [
    "get_rutube_access_key",
    "get_rutube_video_id",
    "get_youtube_video_id",
]
