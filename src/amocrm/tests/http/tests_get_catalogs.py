import pytest

from amocrm.types import AmoCRMCatalog

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def _successful_response(get):
    get.return_value = {
        "_links": {"self": {"href": "/api/v2/catalogs", "method": "get"}},
        "_embedded": {
            "catalogs": [
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
def test_get_catalogs(user, amocrm_client, get):
    got = amocrm_client.get_catalogs()

    assert got == [
        AmoCRMCatalog(id=11271, name="Товары", type="products"),
        AmoCRMCatalog(id=11273, name="Мои юр. лица", type="suppliers"),
    ]
    get.assert_called_once_with(
        url="/api/v4/catalogs",
        params={"limit": 250},
    )
