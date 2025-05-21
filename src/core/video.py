from typing import Protocol
from urllib.parse import parse_qs, urlparse


class VideoModelProtocol(Protocol):
    youtube_id: str | None
    rutube_id: str | None
    rutube_access_key: str | None


class VideoModelMixin:
    def get_youtube_embed_src(self: VideoModelProtocol) -> str:
        return f"https://www.youtube.com/embed/{self.youtube_id}?rel=0"

    def get_youtube_url(self: VideoModelProtocol) -> str:
        if self.youtube_id is not None:
            return f"https://youtu.be/{self.youtube_id}"

        return ""

    def get_rutube_embed_src(self: VideoModelProtocol) -> str:
        if self.rutube_id is None:
            return ""

        if self.rutube_access_key:
            return f"https://rutube.ru/play/embed/{self.rutube_id}/?p={self.rutube_access_key}"
        return f"https://rutube.ru/play/embed/{self.rutube_id}/"

    def get_rutube_url(self: VideoModelProtocol) -> str:
        if self.rutube_id is None:
            return ""

        if self.rutube_access_key:
            return f"https://rutube.ru/video/{self.rutube_id}/?p={self.rutube_access_key}"
        return f"https://rutube.ru/video/{self.rutube_id}/"


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
    "VideoModelMixin",
    "get_rutube_access_key",
    "get_rutube_video_id",
    "get_youtube_video_id",
]
