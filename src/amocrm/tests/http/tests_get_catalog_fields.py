import pytest

from amocrm.types import AmoCRMCatalogField
from amocrm.types import AmoCRMCatalogFieldValue

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.single_thread,
]


@pytest.fixture
def _successful_response(get):
    get.return_value = {
        "_total_items": 5,
        "_page": 1,
        "_page_count": 1,
        "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/catalogs/11271/custom_fields?limit=250&page=1"}},
        "_embedded": {
            "custom_fields": [
                {
                    "id": 2235143,
                    "name": "Артикул",
                    "type": "text",
                    "account_id": 31204626,
                    "code": "SKU",
                    "sort": 510,
                    "is_api_only": False,
                    "enums": None,
                    "catalog_id": 11271,
                    "is_visible": True,
                    "triggers": [],
                    "is_deletable": False,
                    "is_required": False,
                    "search_in": None,
                    "nested": None,
                    "entity_type": "catalogs",
                    "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/catalogs/11271/custom_fields/2235143?limit=250&page=1"}},
                },
                {
                    "id": 2235149,
                    "name": "Группа",
                    "type": "category",
                    "account_id": 31204626,
                    "code": "GROUP",
                    "sort": 511,
                    "is_api_only": False,
                    "enums": None,
                    "catalog_id": 11271,
                    "is_visible": True,
                    "triggers": [],
                    "is_deletable": False,
                    "is_required": False,
                    "search_in": None,
                    "nested": [{"id": 6319, "parent_id": None, "value": "popug", "sort": 0}, {"id": 6321, "parent_id": None, "value": "testtest", "sort": 1}],
                    "entity_type": "catalogs",
                    "_links": {"self": {"href": "https://test.amocrm.ru/api/v4/catalogs/11271/custom_fields/2235149?limit=250&page=1"}},
                },
            ]
        },
    }


@pytest.mark.usefixtures("_successful_response")
def test_get_catalog_fields(user, amocrm_client, get):
    got = amocrm_client.get_catalog_fields(777)

    assert got == [
        AmoCRMCatalogField(id=2235143, name="Артикул", type="text", code="SKU", nested=None),
        AmoCRMCatalogField(
            id=2235149,
            name="Группа",
            type="category",
            code="GROUP",
            nested=[
                AmoCRMCatalogFieldValue(id=6319, value="popug"),
                AmoCRMCatalogFieldValue(id=6321, value="testtest"),
            ],
        ),
    ]
    get.assert_called_once_with(
        url="/api/v4/catalogs/777/custom_fields",
        params={"limit": 250},
    )
