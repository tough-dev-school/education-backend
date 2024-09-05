from typing import Mapping

from django.core.cache import cache

from apps.notion.helpers import get_youtube_video_id
from apps.notion.models import Video
from apps.notion.types import BlockData as NotionBlockData


def get_video_mapping() -> Mapping[str, Mapping[str, str]]:
    cached = cache.get("notion-video-mapping")
    if cached is not None:
        return cached

    mapping = dict()

    for video in Video.objects.all().iterator():
        mapping[video.youtube_id] = {
            "youtube_embed": video.get_youtube_embed_src(),
            "rutube_embed": video.get_rutube_embed_src(),
            "rutube_url": video.get_rutube_url(),
            "youtube_url": video.get_youtube_url(),
        }

    cache.set(key="notion-video-mapping", value=mapping, timeout=60)

    return mapping


def rewrite_video(block_data: NotionBlockData) -> NotionBlockData:
    if "type" not in block_data.get("value", {}):  # skip rewrite for untyped blocks
        return block_data

    if block_data["value"]["type"] != "video":
        return block_data

    video_id = get_youtube_video_id(block_data["value"]["properties"]["source"][0][0])

    if video_id is None:  # skip rewrite for non-youtube videos
        return block_data

    video_mapping = get_video_mapping()

    if video_id in video_mapping:
        block_data["value"]["properties"]["source"] = [[video_mapping[video_id]["rutube_url"]]]
        block_data["value"]["format"]["link_provider"] = "RuTube"
        block_data["value"]["format"]["display_source"] = video_mapping[video_id]["rutube_embed"]

    return block_data
