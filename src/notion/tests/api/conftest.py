import pytest

from notion.block import NotionBlock, NotionBlockList
from notion.page import NotionPage

pytestmark = [pytest.mark.django_db]


@pytest.fixture
def api(api):
    """We test it as normal student, not superuser to check permissions
    """
    api.user.is_superuser = False
    api.user.save()

    return api


@pytest.fixture
def course(mixer):
    return mixer.blend('products.Course')


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
    return mixer.blend('notion.Material', course=course, page_id='0e5693d2173a4f77ae8106813b6e5329')


@pytest.fixture
def page() -> NotionPage:
    return NotionPage(blocks=NotionBlockList([
        NotionBlock(id='block-1', data={'block-name': 'block-1'}),
        NotionBlock(id='block-2', data={'block-name': 'block-2'}),
    ]))


@pytest.fixture(autouse=True)
def fetch_page_recursively(mocker, page: NotionPage):
    return mocker.patch('notion.client.NotionClient.fetch_page_recursively', return_value=page)
