from contextlib import nullcontext as does_not_raise

import pytest

from apps.notion.rewrite import rewrite_notion_so_assets
from apps.notion.types import BlockValue

pytestmark = [pytest.mark.django_db]


def rewrite(block) -> BlockValue:
    return rewrite_notion_so_assets(block)["value"]


@pytest.mark.usefixtures("another_asset")
def test_image_is_rewritten_if_not_in_asset_cache(image):
    assert rewrite(image)["properties"]["source"] == [
        [
            "https://notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2Fd95897d2-8698-468b-ac09-0870070855c9%2Ftypicalmacuser.png?table=test&id=image-block&cache=v2"
        ]
    ]


@pytest.mark.usefixtures("asset")
def test_image_is_not_rewritten_if_asset_is_in_cache(image):
    assert rewrite(image)["properties"]["source"] == [
        ["https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d95897d2-8698-468b-ac09-0870070855c9/typicalmacuser.png"]
    ]


@pytest.mark.usefixtures("another_asset")
def test_page_is_rewritten_if_not_in_asset_cache(page):
    rewritten = rewrite(page)["format"]
    assert (
        rewritten["page_cover"]
        == "https://notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2Fd95897d2-8698-468b-ac09-0870070855c9%2Ftypicalmacuser.png?table=test&id=page-block&cache=v2"
    )
    assert (
        rewritten["page_icon"]
        == "https://notion.so/image/https%3A%2F%2Fs3-us-west-2.amazonaws.com%2Fsecure.notion-static.com%2Fd95897d2-8698-468b-ac09-0870070855c9%2Ftypicalmacuser_icon.png?table=test&id=page-block&cache=v2"
    )


@pytest.mark.usefixtures("asset", "icon_asset")
def test_page_is_not_rewritten_if_cover_and_icon_are_in_asset_cache(page):
    assert (
        rewrite(page)["format"]["page_cover"]
        == "https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d95897d2-8698-468b-ac09-0870070855c9/typicalmacuser.png"
    )
    assert (
        rewrite(page)["format"]["page_icon"]
        == "https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d95897d2-8698-468b-ac09-0870070855c9/typicalmacuser_icon.png"
    )


@pytest.mark.parametrize("param", ["page_cover", "page_icon"])
def test_page_without_cover_and_icon(page, param):
    del page["value"]["format"][param]
    with does_not_raise():
        rewrite(page)
