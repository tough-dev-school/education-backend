from os.path import basename
from urllib.parse import urlparse

from notion.types import BlockId


def page_url_to_id(page_url: str) -> BlockId:
    """Get page id from notion.so URL"""
    url_path = urlparse(page_url).path

    if url_path.endswith('/'):
        url_path = url_path[:-1]

    page_id = basename(url_path)

    return page_id.split('-')[-1]
