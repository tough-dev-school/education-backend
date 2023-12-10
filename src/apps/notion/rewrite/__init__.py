from apps.notion.rewrite.links import rewrite_links
from apps.notion.rewrite.tags import drop_extra_tags
from apps.notion.types import BlockData


def apply_our_adjustments(notion_block_data: BlockData) -> BlockData:
    adjusted = rewrite_links(notion_block_data)

    return drop_extra_tags(adjusted)


__all__ = [
    "apply_our_adjustments",
    "drop_extra_tags",
    "rewrite_links",
]
