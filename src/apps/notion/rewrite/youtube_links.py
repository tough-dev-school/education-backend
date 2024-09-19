from apps.notion.helpers import get_youtube_video_id
from apps.notion.rewrite.video import get_video_mapping
from apps.notion.types import BlockData, TextProperty


def rewrite_youtube_links(notion_block_data: BlockData) -> BlockData:
    if "properties" not in notion_block_data.get("value", {}):
        return notion_block_data

    for key in ("title", "caption"):
        if key in notion_block_data["value"]["properties"]:
            notion_block_data["value"]["properties"][key] = rewrite_prop(notion_block_data["value"]["properties"][key])

    return notion_block_data


def rewrite_prop(prop: TextProperty) -> TextProperty:
    """Drill down notion property data, searching for YouTube link."""
    rewritten = TextProperty()
    mapping = get_video_mapping()

    for value in prop:
        if isinstance(value, list):
            if len(value) >= 1 and value[0] == "a" and isinstance(value[1], str):
                video_id = get_youtube_video_id(value[1])
                if video_id and video_id in mapping:
                    value[1] = mapping[video_id]["rutube_url"]
            else:
                value = rewrite_prop(value)

        rewritten.append(value)

    return rewritten


__all__ = ["rewrite_youtube_links"]
