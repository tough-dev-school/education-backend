from os.path import basename
from urllib.parse import urlparse
from uuid import UUID

from apps.notion.types import NotionId


def page_url_to_id(page_url: str) -> NotionId:
    """Get page id from apps.notion.so URL"""
    url_path = urlparse(page_url).path

    url_path = url_path.removesuffix("/")

    page_id = basename(url_path)

    return page_id.split("-")[-1]


def id_to_uuid(id: NotionId) -> NotionId:
    """Convert notion page id to UUID4"""
    normalized = uuid_to_id(id)
    return f"{normalized[0:8]}-{normalized[8:12]}-{normalized[12:16]}-{normalized[16:20]}-{normalized[20:]}"


def uuid_to_id(uuid: NotionId | UUID) -> NotionId:
    return str(uuid).replace("-", "")
