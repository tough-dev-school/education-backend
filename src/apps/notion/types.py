"""(incomplete) typing for notion responses"""
from typing import Literal, TypedDict

BlockId = str

TextProperty = list[str | list]


class Properties(TypedDict, total=False):
    title: TextProperty
    caption: TextProperty
    last_edited_time: int


class BlockValue(TypedDict, total=False):
    id: BlockId
    content: list[BlockId]
    last_edited_time: int
    properties: Properties
    type: Literal[
        "page",
        "text",
        "bookmark",
        "callout",
        "code",
        "column",
        "column_list",
        "decorator",
        "equation",
        "header",
        "image",
        "divider",
        "sub_header",
        "sub_sub_header",
        "bulleted_list",
        "numbered_list",
    ]


class BlockData(TypedDict, total=False):
    role: str
    value: BlockValue


__all__ = [
    "BlockId",
    "BlockData",
    "TextProperty",
]
