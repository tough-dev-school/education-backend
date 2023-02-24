from typing import Any, Mapping

import contextlib
from functools import lru_cache

from notion.helpers import uuid_to_id
from notion.models import Material


@lru_cache
def get_rewrite_mapping() -> Mapping[str, str]:
    """Returns a mapping Notion Material -> our slug"""
    mapping = Material.objects.all().values_list('page_id', 'slug')

    return {page_id: uuid_to_id(str(slug)) for page_id, slug in mapping}


def rewrite(notion_block_data: dict[str, Any]) -> dict[str, Any]:
    if 'properties' not in notion_block_data.get('value', {}):
        return notion_block_data

    for key in ['title', 'caption']:
        if key in notion_block_data['value']['properties']:
            notion_block_data['value']['properties'][key] = rewrite_prop(notion_block_data['value']['properties'][key])

    return notion_block_data


def rewrite_prop(prop: list) -> list[str]:  # NOQA: CCR001
    """Drill down notion property data, searching for a link to the internal material.
    If the link is found -- rewrite its id to our material slug
    """
    rewritten: list = list()
    rewrite_mapping = get_rewrite_mapping()

    for i, value in enumerate(prop):
        if isinstance(value, list):
            if len(value) >= 1 and value[0] == 'a' and value[1].startswith('/'):
                with contextlib.suppress(KeyError):  # blocks not in mapping remain not rewritten
                    value[1] = '/' + rewrite_mapping[value[1].replace('/', '')]
            else:
                value = rewrite_prop(prop[i])

        rewritten.append(value)

    return rewritten
