import fnmatch

from benedict import benedict

from apps.notion.types import BlockData

TAGS_TO_LIVE = (
    "value.id",
    "value.type",
    "value.content.*",
    "value.properties.*",
    "value.format.page_icon",
    "value.format.page_cover",
    "value.format.page_cover_position",
    "value.parent_id",
    "value.parent_table",
)


def drop_extra_tags(notion_block_data: BlockData) -> BlockData:
    data = benedict(notion_block_data)
    for key in sorted(data.keypaths(), key=len, reverse=True):
        if not tag_should_live(key):
            del data[key]

    return notion_block_data


def tag_should_live(tag: str) -> bool:
    for tag_to_live in TAGS_TO_LIVE:
        if tag_to_live.startswith(f"{tag}."):
            return True

        if fnmatch.fnmatch(tag, tag_to_live) or tag == tag_to_live.replace(".*", ""):
            return True

    return False
