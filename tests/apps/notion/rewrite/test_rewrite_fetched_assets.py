import pytest
from apps.notion.types import BlockValue
from apps.notion.models import NotionAsset
from apps.notion.rewrite import rewrite_fetched_assets
from apps.notion.rewrite.fetched_assets import get_asset_mapping
from contextlib import nullcontext as does_not_raise

pytestmark = [pytest.mark.django_db]


def rewrite(block) -> BlockValue:
    return rewrite_fetched_assets(block)["value"]


@pytest.fixture
def image():
    return {
        "value": {
            "type": "image",
            "properties": {
                "size": [[ "228KB" ]],
                "source": [[ "https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d95897d2-8698-468b-ac09-0870070855c9/typicalmacuser.png"]],
            },
        },
    }

@pytest.fixture
def page():
    return {
        "value": {
            "type": "page",
            "format": {
                "page_cover": "https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d95897d2-8698-468b-ac09-0870070855c9/typicalmacuser.png",
                "page_icon": "https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d95897d2-8698-468b-ac09-0870070855c9/typicalmacuser_icon.png",
            },
        },
    }

@pytest.fixture(autouse=True)
def _isolate_rewrite_mapping_cache():
    """get_asset_mapping() is LRU-cached, so we need to reset it after year test run"""
    yield
    get_asset_mapping.cache_clear()


@pytest.fixture
def asset() -> NotionAsset:
    return NotionAsset.objects.create(
        url="https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d95897d2-8698-468b-ac09-0870070855c9/typicalmacuser.png",
        file="assets/macuser.png",
        size=100,
        md5_sum='DEADBEEF',
    )

@pytest.fixture
def icon_asset() -> NotionAsset:
    return NotionAsset.objects.create(
        url="https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d95897d2-8698-468b-ac09-0870070855c9/typicalmacuser_icon.png",
        file="assets/macuser_icon.png",
        size=100,
        md5_sum='DEADBEEF',
    )

@pytest.fixture
def another_asset() -> NotionAsset:
    return NotionAsset.objects.create(
        url="https://some-other.url/test.png",
        file="assets/macuser.png",
        size=100,
        md5_sum='DEADBEEF',
    )


@pytest.mark.usefixtures("another_asset")
def test_image_not_rewritten(image):
    assert rewrite(image)["properties"]["source"] == [["https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d95897d2-8698-468b-ac09-0870070855c9/typicalmacuser.png"]]


@pytest.mark.usefixtures("asset")
def test_image_rewritten(image):
    assert rewrite(image)["properties"]["source"] == [["/media/assets/macuser.png"]]


@pytest.mark.usefixtures("another_asset")
def test_page_not_rewritten(page):
    assert rewrite(page)["format"]["page_cover"] == "https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d95897d2-8698-468b-ac09-0870070855c9/typicalmacuser.png"
    assert rewrite(page)["format"]["page_icon"] == "https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d95897d2-8698-468b-ac09-0870070855c9/typicalmacuser_icon.png"


@pytest.mark.usefixtures("asset", "icon_asset")
def test_page_rewritten(page):
    assert rewrite(page)["format"]["page_cover"] == "/media/assets/macuser.png"
    assert rewrite(page)["format"]["page_icon"] == "/media/assets/macuser_icon.png"


@pytest.mark.parametrize("param", ["page_cover", "page_icon"])
def test_page_without_cover_and_icon(page, param):
    del page["value"]["format"][param]
    with does_not_raise():
        rewrite(page)
