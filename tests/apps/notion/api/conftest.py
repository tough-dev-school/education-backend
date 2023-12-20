import pytest
from apps.notion.block import NotionBlock

from apps.notion.page import NotionPage

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def api(api):
    """We test it as normal student, not superuser to check permissions"""
    api.user.update(is_superuser=False)

    return api


@pytest.fixture(autouse=True)
def order(factory, course, mocker, api):
    mocker.patch("apps.orders.services.order_shipper.OrderShipper.write_success_admin_log")

    return factory.order(
        user=api.user,
        item=course,
        is_paid=True,
    )


@pytest.fixture
def unpaid_order(order):
    order.refund()

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
def mock_notion_response(mocker, page: NotionPage):
    return mocker.patch("apps.notion.client.NotionClient.fetch_page_recursively", return_value=page)
