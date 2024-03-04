from hashlib import md5
from os.path import basename
from urllib.parse import quote

from django.core.files.base import ContentFile

from apps.notion.models import NotionAsset
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


def save_asset(url: str, original_url: str) -> None:
    """Saves asset with `url` as NotionAsset with `original_url` as a key"""
    from apps.notion.client import NotionClient

    fetched = NotionClient.fetch_asset(url)
    hashsum = md5(fetched).hexdigest()

    asset, created = NotionAsset.objects.get_or_create(
        url=original_url,
        defaults={
            "size": len(fetched),
            "md5_sum": hashsum,
        },
    )
    if not created and asset.md5_sum == hashsum:  # do not query s3 if asset is not changed
        return

    asset.file.save(
        name=basename(original_url),  # will be randomized by RandomFileName
        content=ContentFile(fetched),
    )


def is_notion_url(url: str) -> bool:
    return any(notion_url in url for notion_url in NOTION_URLS)


__all__ = [
    "get_asset_url",
    "is_notion_url",
    "save_asset",
]
