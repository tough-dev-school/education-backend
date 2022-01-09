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


def id_to_uuid(id: BlockId) -> str:
    """Convert notion page id to UUID4"""
    normalized = id.replace('-', '')
    return f'{normalized[0:8]}-{normalized[8:12]}-{normalized[12:16]}-{normalized[16:20]}-{normalized[20:]}'
