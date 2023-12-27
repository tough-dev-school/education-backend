from functools import lru_cache

from apps.notion.assets import get_asset_url
from apps.notion.models import NotionAsset
from apps.notion.types import BlockData as NotionBlockData


@lru_cache
def get_already_fetched_assets() -> list[str]:
    return NotionAsset.objects.all().values_list("url", flat=True)  # type: ignore


def rewrite_notion_so_assets(block_data: NotionBlockData) -> NotionBlockData:
    if "type" not in block_data.get("value", {}):
        return block_data

    if block_data["value"]["type"] == "image":
        return rewrite_image(block_data)

    if block_data["value"]["type"] == "page":
        return rewrite_page(block_data)

    return block_data


def rewrite_image(block_data: NotionBlockData) -> NotionBlockData:
    already_fetched_assets = get_already_fetched_assets()
    original_src = block_data["value"]["properties"]["source"][0][0]

    if original_src not in already_fetched_assets:
        block_data["value"]["properties"]["source"] = [
            [
                get_asset_url(
                    asset=original_src,
                    block_data=block_data,
                )
            ]
        ]

    return block_data


def rewrite_page(block_data: NotionBlockData) -> NotionBlockData:
    already_fetched_assets = get_already_fetched_assets()

    cover_src = block_data["value"].get("format", {}).get("page_cover")
    if cover_src is not None and cover_src not in already_fetched_assets:
        block_data["value"]["format"]["page_cover"] = get_asset_url(
            asset=cover_src,
            block_data=block_data,
        )

    icon_src = block_data["value"].get("format", {}).get("page_icon")
    if icon_src is not None and icon_src not in already_fetched_assets:
        block_data["value"]["format"]["page_icon"] = get_asset_url(
            asset=icon_src,
            block_data=block_data,
        )

    return block_data
