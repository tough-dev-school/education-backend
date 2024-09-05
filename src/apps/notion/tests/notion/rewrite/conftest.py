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


@pytest.fixture
def youtube_video() -> dict:
    return {
        "value": {
            "id": "video_block",
            "type": "video",
            "format": {
                "block_width": 1280,
                "link_author": "Школа сильных программистов",
                "link_provider": "YouTube",
                "display_source": "https://www.youtube.com/embed/dVo80vW4ekw?rel=0",
            },
            "version": 1,
            "properties": {"source": [["https://youtu.be/dVo80vW4ekw"]]},
            "created_time": 1723019010455,
            "parent_table": "block",
            "last_edited_time": 1723019010455,
        }
    }


@pytest.fixture
def non_youtube_video():
    return {
        "value": {
            "id": "video_block",
            "type": "video",
            "format": {
                "block_width": 1280,
                "link_author": "Школа сильных программистов",
                "link_provider": "YouTube",
                "display_source": "https://s3-us-west-2.amazonaws.com/secure.notion-static.com/9294be93-51f7-4b61-b330-cdf098234a34/diagrams.mp4",
            },
            "version": 1,
            "properties": {"source": [["https://s3-us-west-2.amazonaws.com/secure.notion-static.com/9294be93-51f7-4b61-b330-cdf098234a34/diagrams.mp4"]]},
            "created_time": 1723019010455,
            "parent_table": "block",
            "last_edited_time": 1723019010455,
        }
    }
