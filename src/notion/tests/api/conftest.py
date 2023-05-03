import pytest

from notion.block import NotionBlock
from notion.block import NotionBlockList
from notion.page import NotionPage

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def api(api):
    """We test it as normal student, not superuser to check permissions"""
    api.user.is_superuser = False
    api.user.save()

    return api


@pytest.fixture
def course(mixer):
    return mixer.blend("products.Course")


@pytest.fixture(autouse=True)
def order(factory, course, api):
    return factory.order(
        user=api.user,
        item=course,
        is_paid=True,
    )


@pytest.fixture
def unpaid_order(order):
    order.set_not_paid()

    return order


@pytest.fixture(autouse=True)
def material(mixer, course):
    return mixer.blend(
        "notion.Material",
        course=course,
        page_id="0e5693d2173a4f77ae8106813b6e5329",
        slug="4d5726e8ee524448b8f97be4c7f8e632",
    )


@pytest.fixture
def page() -> NotionPage:
    return NotionPage(
        blocks=NotionBlockList(
            [
                NotionBlock(id="block-1", data={"role": "reader-1", "value": {"last_edited_time": 1642356660000}}),
                NotionBlock(id="block-2", data={"role": "reader-2"}),
            ]
        )
    )


@pytest.fixture
def mock_notion_response(mocker, page: NotionPage):
    return mocker.patch("notion.client.NotionClient.fetch_page_recursively", return_value=page)


@pytest.fixture
def _disable_notion_cache(mocker):
    mocker.patch("notion.cache.cache_disabled", return_value=True)
