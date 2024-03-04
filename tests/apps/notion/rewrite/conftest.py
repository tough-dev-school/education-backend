import pytest

from apps.notion.models import NotionAsset


@pytest.fixture
def image():
    return {
        "value": {
            "id": "image-block",
            "type": "image",
            "properties": {
                "size": [["228KB"]],
                "source": [["https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d95897d2-8698-468b-ac09-0870070855c9/typicalmacuser.png"]],
            },
            "parent_table": "test",
        },
    }


@pytest.fixture
def page():
    return {
        "value": {
            "id": "page-block",
            "type": "page",
            "format": {
                "page_cover": "https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d95897d2-8698-468b-ac09-0870070855c9/typicalmacuser.png",
                "page_icon": "https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d95897d2-8698-468b-ac09-0870070855c9/typicalmacuser_icon.png",
            },
            "parent_table": "test",
        },
    }


@pytest.fixture
def asset() -> NotionAsset:
    """Fetched asset"""
    return NotionAsset.objects.create(
        url="https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d95897d2-8698-468b-ac09-0870070855c9/typicalmacuser.png",
        file="assets/macuser.png",
        size=100,
        md5_sum="DEADBEEF",
    )


@pytest.fixture
def icon_asset() -> NotionAsset:
    """Another fetched asset"""
    return NotionAsset.objects.create(
        url="https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d95897d2-8698-468b-ac09-0870070855c9/typicalmacuser_icon.png",
        file="assets/macuser_icon.png",
        size=100,
        md5_sum="DEADBEEF",
    )


@pytest.fixture
def another_asset() -> NotionAsset:
    """Yet another asset never seen in page and image blocks"""
    return NotionAsset.objects.create(
        url="https://some-other.url/test.png",
        file="assets/macuser.png",
        size=100,
        md5_sum="DEADBEEF",
    )
