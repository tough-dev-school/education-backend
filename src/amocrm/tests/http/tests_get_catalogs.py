import pytest

from amocrm.types import AmoCRMCatalogField

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def _successful_response(get):
    get.return_value = {
        "_links": {"self": {"href": "/api/v2/catalogs", "method": "get"}},
        "_embedded": {
            "items": [
                {
                    "id": 11271,
                    "name": "Товары",
                    "created_by": 9898394,
                    "created_at": 1690790026,
                    "sort": 0,
                    "type": "products",
                    "can_add_elements": True,
                    "can_show_in_cards": True,
                    "can_link_multiple": True,
                    "sdk_widget_code": None,
                    "widgets": [],
                    "_links": {"self": {"href": "/api/v2/catalogs?id=11271", "method": "get"}},
                },
                {
                    "id": 11273,
                    "name": "Мои юр. лица",
                    "created_by": 9898394,
                    "created_at": 1690790026,
                    "sort": 0,
                    "type": "suppliers",
                    "can_add_elements": True,
                    "can_show_in_cards": True,
                    "can_link_multiple": True,
                    "sdk_widget_code": None,
                    "widgets": [],
                    "_links": {"self": {"href": "/api/v2/catalogs?id=11273", "method": "get"}},
                },
            ]
        },
    }


@pytest.mark.usefixtures("_successful_response")
def test_create_customer_request_fields(user, amocrm_client, get):
    got = amocrm_client.get_catalogs()

    assert got == [
        AmoCRMCatalogField(id=11271, name="Товары", type="products"),
        AmoCRMCatalogField(id=11273, name="Мои юр. лица", type="suppliers"),
    ]
    get.assert_called_once_with(
        url="/api/v2/catalogs",
        params={"limit": 250},
    )
