import contextlib
from functools import lru_cache
from typing import Mapping

from notion.helpers import uuid_to_id
from notion.models import Material
from notion.types import BlockData
from notion.types import BlockId
from notion.types import TextProperty


@lru_cache
def get_rewrite_mapping() -> Mapping[BlockId, BlockId]:
    """Returns a mapping Notion Material -> our slug"""
    mapping = Material.objects.all().values_list("page_id", "slug")

    return {page_id: uuid_to_id(str(slug)) for page_id, slug in mapping}


def rewrite(notion_block_data: BlockData) -> BlockData:
    if "properties" not in notion_block_data.get("value", {}):
        return notion_block_data

    for key in ("title", "caption"):
        if key in notion_block_data["value"]["properties"]:
            notion_block_data["value"]["properties"][key] = rewrite_prop(notion_block_data["value"]["properties"][key])  # type: ignore

    return notion_block_data


def rewrite_prop(prop: TextProperty) -> TextProperty:  # NOQA: CCR001
    """Drill down notion property data, searching for a link to the internal material.
    If the link is found -- rewrite its id to our material slug
    """
    rewritten = TextProperty()
    mapping = get_rewrite_mapping()

    for value in prop:
        if isinstance(value, list):
            if len(value) >= 1 and value[0] == "a" and isinstance(value[1], str) and value[1].startswith("/"):  # it is a link, and the link is internal
                with contextlib.suppress(KeyError):  # blocks not in mapping remain not rewritten
                    value[1] = "/" + mapping[value[1].replace("/", "")]
            else:
                value = rewrite_prop(value)

        rewritten.append(value)

    return rewritten
