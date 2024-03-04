import fnmatch

from benedict import benedict

from apps.notion.types import BlockData

TAGS_WHITELIST = (
    "value.id",
    "value.type",
    "value.content.*",
    "value.properties.*",
    "value.format.*",
    "value.parent_id",
    "value.parent_table",
)


def drop_extra_tags(notion_block_data: BlockData) -> BlockData:
    data = benedict(notion_block_data)
    for key in sorted(data.keypaths(), key=len, reverse=True):
        if not whitelisted(key):
            del data[key]

    return notion_block_data


def whitelisted(tag: str) -> bool:
    for whitelist_entry in TAGS_WHITELIST:
        if whitelist_entry.startswith(f"{tag}."):
            return True

        if fnmatch.fnmatch(tag, whitelist_entry) or tag == whitelist_entry.replace(".*", ""):
            return True

    return False
