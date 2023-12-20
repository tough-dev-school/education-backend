import pytest
from apps.notion.block import NotionBlock
from apps.notion.models import NotionAsset
from apps.notion import exceptions
from celery.exceptions import Retry


pytestmark = [pytest.mark.django_db]


@pytest.fixture
def page():
    return NotionBlock(id="test-block", data={
        "value": {
            "id": "test-block",
            "type": "page",
            "format": {
                "page_cover": "secure.notion-static.com/typicalmacuser.jpg",
            },
            "parent_table": "100500",
        }
    })

@pytest.fixture
def image():
    return NotionBlock(id="test-block", data={
        "value": {
            "id": "test-block",
            "type": "image",
            "properties": {
                "size": [["100x500"]],
                "source": [["secure.notion-static.com/typicalmacuser.jpg"]],
            },
            "parent_table": "100500",
        }
    })


@pytest.fixture(autouse=True)
def _mock_middleware_response(respx_mock):
    respx_mock.get(url="http://notion.middleware/v1/asset/?url=https:%2F%2Fnotion.so%2Fimage%2Fsecure.notion-static.com%252Ftypicalmacuser.jpg?table=100500&id=test-block&cache=v2").respond(content=b"test-img-content")
    respx_mock.get(url="http://notion.middleware/v1/asset/?url=https:%2F%2Fnotion.so%2Fimage%2Fsecure.notion-static.com%252Ftypicalmacuser_icon.jpg?table=100500&id=test-block&cache=v2").respond(content=b"test-icon-content")


def test_image(image):
    image.save_assets()

    asset = NotionAsset.objects.get(url="secure.notion-static.com/typicalmacuser.jpg")

    assert asset.file.read() == b"test-img-content"


def test_page_cover(page):
    page.save_assets()

    asset = NotionAsset.objects.get(url="secure.notion-static.com/typicalmacuser.jpg")

    assert asset.file.read() == b"test-img-content"


def test_page_cover_and_icon_are_both_fetched(page):
    page.data["value"]["format"]["page_icon"] = "secure.notion-static.com/typicalmacuser_icon.jpg"

    page.save_assets()

    assert NotionAsset.objects.count() == 2  # make sure both assets are fetched


def test_failure(image, respx_mock):
    respx_mock.get(url="http://notion.middleware/v1/asset/?url=https:%2F%2Fnotion.so%2Fimage%2Fsecure.notion-static.com%252Ftypicalmacuser.jpg?table=100500&id=test-block&cache=v2").respond(status_code=400)

    with pytest.raises(Retry):
        image.save_assets()
