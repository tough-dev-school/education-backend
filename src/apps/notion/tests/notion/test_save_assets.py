import pytest
from celery.exceptions import Retry

from apps.notion.block import NotionBlock
from apps.notion.models import NotionAsset

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def page():
    return NotionBlock(
        id="test-block",
        data={
            "value": {
                "id": "test-block",
                "type": "page",
                "format": {
                    "page_cover": "secure.notion-static.com/typicalmacuser.jpg",
                },
                "parent_table": "100500",
            }
        },
    )


@pytest.fixture
def image():
    return NotionBlock(
        id="test-block",
        data={
            "value": {
                "id": "test-block",
                "type": "image",
                "properties": {
                    "size": [["100x500"]],
                    "source": [["secure.notion-static.com/typicalmacuser.jpg"]],
                },
                "parent_table": "100500",
            }
        },
    )


@pytest.fixture(autouse=True)
def _mock_middleware_response(respx_mock):
    respx_mock.post(url="http://notion.middleware/v1/asset/").respond(content=b"test-img-content")


def test_image(image):
    image.save_assets()

    asset = NotionAsset.objects.get(url="secure.notion-static.com/typicalmacuser.jpg")

    assert asset.file.read() == b"test-img-content"
    assert asset.size == 16
    assert asset.md5_sum == "c87337eddb4771e90e429e8c34d178a4"


def test_page_cover(page):
    page.save_assets()

    asset = NotionAsset.objects.get(url="secure.notion-static.com/typicalmacuser.jpg")

    assert asset.file.read() == b"test-img-content"
    assert asset.size == 16
    assert asset.md5_sum == "c87337eddb4771e90e429e8c34d178a4"


def test_page_cover_and_icon_are_both_fetched(page):
    page.data["value"]["format"]["page_icon"] = "secure.notion-static.com/typicalmacuser_icon.jpg"

    page.save_assets()

    assert NotionAsset.objects.count() == 2  # make sure both assets are fetched


@pytest.mark.parametrize(
    ("hash", "should_not_override"),
    [
        ("c87337eddb4771e90e429e8c34d178a4", True),
        ("not-so-hashy", False),
    ],
)
def test_asset_is_not_overiden(image, mocker, hash, should_not_override):
    NotionAsset.objects.create(url="secure.notion-static.com/typicalmacuser.jpg", md5_sum=hash, size=16)
    save = mocker.spy(NotionAsset, "save")

    image.save_assets()

    assert (save.call_count == 0) is should_not_override


def test_failure(image, respx_mock):
    respx_mock.post(url="http://notion.middleware/v1/asset/").respond(status_code=400)

    with pytest.raises(Retry):
        image.save_assets()
