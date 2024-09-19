from apps.notion.rewrite.fetched_assets import rewrite_fetched_assets
from apps.notion.rewrite.links import rewrite_links
from apps.notion.rewrite.notion_so_assets import rewrite_notion_so_assets
from apps.notion.rewrite.tags import drop_extra_tags
from apps.notion.rewrite.video import rewrite_video
from apps.notion.rewrite.youtube_links import rewrite_youtube_links
from apps.notion.types import BlockData
from core.request import get_request


def apply_our_adjustments(notion_block_data: BlockData) -> BlockData:
    adjusted = rewrite_links(notion_block_data)  # replace material ids
    adjusted = drop_extra_tags(adjusted)  # remove tags not needed in frontend rendering
    adjusted = rewrite_fetched_assets(adjusted)  # replace asset links with links to our cdn

    request = get_request()
    if request is not None and request.country_code == "RU":
        if "frkn" in request.headers:
            adjusted = rewrite_video(adjusted)  # apply video adjustments for russian users
            adjusted = rewrite_youtube_links(adjusted)

    return rewrite_notion_so_assets(adjusted)  # rewrite remaining assets to go though notion.so so they would sign our request to their S3


__all__ = [
    "apply_our_adjustments",
    "drop_extra_tags",
    "rewrite_fetched_assets",
    "rewrite_links",
    "rewrite_notion_so_assets",
    "rewrite_video",
    "rewrite_youtube_links",
]
