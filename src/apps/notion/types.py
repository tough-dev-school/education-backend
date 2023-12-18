"""(incomplete) typing for notion responses"""
from typing import Literal, TypedDict

BlockId = str
BlockType = Literal[
    "alias",
    "bookmark",
    "bulleted_list",
    "callout",
    "code",
    "collection_view",
    "column",
    "column_list",
    "copy_indicator",
    "divider",
    "external_object_instance",
    "file",
    "header",
    "image",
    "numbered_list",
    "page",
    "quote",
    "sub_header",
    "sub_sub_header",
    "table",
    "table_of_contents",
    "table_row",
    "text",
    "to_do",
    "toggle",
    "transclusion_container",
    "transclusion_reference",
    "video",
]

TextProperty = list[str | list]


class BlockValue(TypedDict, total=False):
    id: BlockId
    content: list[BlockId]
    parent_id: str
    parent_table: str
    properties: dict[str, TextProperty]
    type: BlockType


class BlockData(TypedDict, total=False):
    role: str
    value: BlockValue


class BlockProperties(TypedDict, total=False):
    title: str
    caption: str
    size: str
    language: str
    source: str


__all__ = [
    "BlockId",
    "BlockData",
    "BlockProperties",
    "BlockType",
    "TextProperty",
]
