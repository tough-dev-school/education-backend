from urllib.parse import quote

from apps.notion.types import BlockData as NotionBlockData
from core.helpers import append_to_query_string

NOTION_URLS = (
    "secure.notion-static.com",
    "prod-files-secure",
)


def get_asset_url(asset: str, block_data: NotionBlockData) -> str:
    """Get https://notion.so url to download from their signed storage"""
    if not is_notion_url(asset):
        return asset

    source = quote(asset, safe="")
    asset_type = block_data["value"]["type"]
    if asset_type == "page":
        asset_type = "image"

    table = block_data["value"]["parent_table"]
    if table == "space":
        table = "block"

    return append_to_query_string(
        url=f"https://notion.so/{asset_type}/{source}",
        table=table,
        id=block_data["value"]["id"],
        cache="v2",
    )


def is_notion_url(url: str) -> bool:
    return any(notion_url in url for notion_url in NOTION_URLS)
