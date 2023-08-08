import pytest

from amocrm.types import AmoCRMEntityLink

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def _successful_response(post):
    post.return_value = {
        "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/customers/1590745/links"}},
        "_embedded": {"links": [{"to_entity_id": 71462075, "to_entity_type": "contacts", "metadata": None}]},
    }


@pytest.fixture
def entity_to_link():
    return AmoCRMEntityLink(to_entity_id=71462075, to_entity_type="contacts")


@pytest.mark.usefixtures("_successful_response")
@pytest.mark.parametrize("entity_type", ["leads", "contacts", "companies", "customers", "catalog_elements"])
def test_create_catalog_element_post_correct_params(amocrm_client, post, entity_to_link, entity_type):
    amocrm_client.link_entity_to_another_entity(entity_type=entity_type, entity_id=1590745, entity_to_link=entity_to_link)

    post.assert_called_once_with(
        url=f"/api/v4/{entity_type}/1590745/link",
        data=[
            {
                "to_entity_id": 71462075,
                "to_entity_type": "contacts",
            },
        ],
    )
