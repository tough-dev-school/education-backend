from functools import lru_cache
from typing import Mapping

from apps.notion.models import NotionAsset
from apps.notion.types import BlockData as NotionBlockData


@lru_cache
def get_asset_mapping() -> Mapping[str, str]:
    return {asset.url: asset.get_absolute_url() for asset in NotionAsset.objects.all().iterator()}


def rewrite_fetched_assets(block_data: NotionBlockData) -> NotionBlockData:
    if "type" not in block_data.get("value", {}):
        return block_data

    if block_data["value"]["type"] == "image":
        return rewrite_image(block_data)

    if block_data["value"]["type"] == "page":
        return rewrite_page(block_data)

    return block_data


def rewrite_image(block_data: NotionBlockData) -> NotionBlockData:
    asset_maping = get_asset_mapping()
    original_src = block_data["value"]["properties"]["source"][0][0]

    if original_src in asset_maping:
        block_data["value"]["properties"]["source"] = [[asset_maping[original_src]]]

    return block_data


def rewrite_page(block_data: NotionBlockData) -> NotionBlockData:
    asset_mapping = get_asset_mapping()

    cover_src = block_data["value"].get("format", {}).get("page_cover")
    if cover_src is not None and cover_src in asset_mapping:
        block_data["value"]["format"]["page_cover"] = asset_mapping[cover_src]

    icon_src = block_data["value"].get("format", {}).get("page_icon")
    if icon_src is not None and icon_src in asset_mapping:
        block_data["value"]["format"]["page_icon"] = asset_mapping[icon_src]

    return block_data
